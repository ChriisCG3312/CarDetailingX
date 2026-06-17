from django.views.generic import TemplateView
from django.utils import timezone
from django.contrib import messages

from django.db.models import (
    Sum,
    Count,
    Avg,
    F,
    Q,
    ExpressionWrapper,
    DurationField,
)
from django.db.models.functions import TruncDate

from apps.usuarios.mixins import AdminRequiredMixin
from apps.citas.models import Cita, Pago
from apps.seguimiento.models import Seguimiento

from .utils import obtener_rango_fechas
from django.views import View

from .exports import (
    generar_pdf_tabla,
    generar_excel_tabla,
)


class MainDashboardView(AdminRequiredMixin, TemplateView):
    """Dashboard principal del sistema."""
    template_name = "usuarios/dashboard.html"


class DashboardView(AdminRequiredMixin, TemplateView):
    """
    Dashboard principal del módulo de reportes.
    Muestra estadísticas rápidas del sistema.
    """
    template_name = "reportes/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        hoy = timezone.localdate()
        inicio_mes = hoy.replace(day=1)

        ingresos_mes = (
            Pago.objects.filter(
                pagado_en__date__range=(inicio_mes, hoy)
            ).aggregate(total=Sum("monto"))["total"]
            or 0
        )

        citas_pendientes_hoy = Cita.objects.filter(
            fecha_hora__date=hoy,
            estado=Cita.Estado.PENDIENTE
        ).count()

        context["ingresos_mes"] = ingresos_mes
        context["citas_pendientes_hoy"] = citas_pendientes_hoy

        return context


class ReporteIngresosView(AdminRequiredMixin, TemplateView):
    """Reporte de ingresos del taller. Permite filtrar por fechas y método de pago."""
    template_name = "reportes/ingresos.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        fecha_inicio, fecha_fin = obtener_rango_fechas(self.request)

        if fecha_fin < fecha_inicio:
            messages.error(self.request, "La fecha fin debe ser posterior a la fecha de inicio")
            context["error"] = True
            return context

        metodo = self.request.GET.get("metodo")

        pagos = Pago.objects.filter(pagado_en__date__range=(fecha_inicio, fecha_fin))

        if metodo:
            pagos = pagos.filter(metodo=metodo)

        total_ingresos = pagos.aggregate(total=Sum("monto"))["total"] or 0

        ingresos_por_dia = (
            pagos
            .annotate(dia=TruncDate("pagado_en"))
            .values("dia")
            .annotate(total=Sum("monto"))
            .order_by("dia")
        )

        ingresos_por_metodo = (
            pagos
            .values("metodo")
            .annotate(total=Sum("monto"))
            .order_by("metodo")
        )

        context.update({
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "metodo": metodo,
            "pagos": pagos.select_related("cita", "cita__cliente", "cita__paquete"),
            "total_ingresos": total_ingresos,
            "ingresos_por_dia": list(ingresos_por_dia),
            "ingresos_por_metodo": list(ingresos_por_metodo),
            "sin_datos": not pagos.exists(),
        })

        return context


class ReporteCitasEstadoView(AdminRequiredMixin, TemplateView):
    """Reporte de citas agrupadas por estado."""
    template_name = "reportes/citas_estado.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        fecha_inicio, fecha_fin = obtener_rango_fechas(self.request)

        if fecha_fin < fecha_inicio:
            messages.error(self.request, "La fecha fin debe ser posterior a la fecha de inicio")
            context["error"] = True
            return context

        citas = Cita.objects.filter(fecha_hora__date__range=(fecha_inicio, fecha_fin))

        datos_estado = (
            citas
            .values("estado")
            .annotate(total=Count("id"))
            .order_by("estado")
        )

        total_citas = citas.count()
        resultados = []

        for item in datos_estado:
            porcentaje = (item["total"] * 100 / total_citas) if total_citas > 0 else 0
            resultados.append({
                "estado": item["estado"],
                "total": item["total"],
                "porcentaje": round(porcentaje, 2),
            })

        canceladas = citas.filter(estado=Cita.Estado.CANCELADA).count()
        tasa_cancelacion = round((canceladas * 100 / total_citas), 2) if total_citas > 0 else 0

        context.update({
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "total_citas": total_citas,
            "datos_estado": resultados,
            "tasa_cancelacion": tasa_cancelacion,
            "sin_datos": total_citas == 0,
        })

        return context


class ReporteServiciosTopView(AdminRequiredMixin, TemplateView):
    """Reporte de los paquetes más solicitados."""
    template_name = "reportes/servicios_top.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        fecha_inicio, fecha_fin = obtener_rango_fechas(self.request, dias_default=30)

        if fecha_fin < fecha_inicio:
            messages.error(self.request, "La fecha fin debe ser posterior a la fecha de inicio")
            context["error"] = True
            return context

        paquetes_top = (
            Cita.objects
            .filter(fecha_hora__date__range=(fecha_inicio, fecha_fin))
            .values("paquete_id", "paquete__nombre")
            .annotate(
                total_citas=Count("id"),
                ingresos=Sum("pago__monto", filter=Q(estado=Cita.Estado.TERMINADA)),
            )
            .order_by("-total_citas")[:10]
        )

        resultados = [
            {
                "nombre": p["paquete__nombre"],
                "total_citas": p["total_citas"],
                "ingresos": p["ingresos"] or 0,
            }
            for p in paquetes_top
        ]

        context.update({
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "servicios": resultados,
            "sin_datos": len(resultados) == 0,
        })

        return context

class ReporteTecnicosView(AdminRequiredMixin, TemplateView):
    """Reporte de desempeño de técnicos."""
    template_name = "reportes/tecnicos.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        fecha_inicio, fecha_fin = obtener_rango_fechas(self.request)

        if fecha_fin < fecha_inicio:
            messages.error(self.request, "La fecha fin debe ser posterior a la fecha de inicio")
            context["error"] = True
            return context

        tecnicos = (
            Seguimiento.objects
            .filter(
                estado=Seguimiento.Estado.ENTREGADO,
                actualizado_en__date__range=(fecha_inicio, fecha_fin),
            )
            .annotate(
                duracion=ExpressionWrapper(
                    F("actualizado_en") - F("creado_en"),
                    output_field=DurationField()
                )
            )
            .values("tecnico__first_name", "tecnico__last_name")
            .annotate(
                total_servicios=Count("id"),
                tiempo_promedio=Avg("duracion"),
            )
            .order_by("-total_servicios")
        )

        context.update({
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "tecnicos": tecnicos,
            "sin_datos": not tecnicos.exists(),
        })

        return context



class ExportarIngresosPDFView(AdminRequiredMixin, View):
    """Exporta el reporte de ingresos a PDF."""

    def get(self, request, *args, **kwargs):
        fecha_inicio, fecha_fin = obtener_rango_fechas(request)

        pagos = Pago.objects.select_related(
            "cita", "cita__cliente", "cita__paquete"
        ).filter(pagado_en__date__range=(fecha_inicio, fecha_fin))

        filas = [
            [
                pago.cita.id,
                str(pago.cita.cliente),
                str(pago.cita.paquete),
                pago.metodo.title(),
                pago.monto,
                pago.pagado_en.strftime("%d/%m/%Y"),
            ]
            for pago in pagos
        ]

        return generar_pdf_tabla(
            titulo="Reporte de ingresos",
            subtitulo=f"Periodo: {fecha_inicio:%d/%m/%Y} - {fecha_fin:%d/%m/%Y}",
            encabezados=["Cita", "Cliente", "Paquete", "Método", "Monto", "Fecha de pago"],
            filas=filas,
            nombre_archivo="reporte_ingresos",
        )


class ExportarIngresosExcelView(AdminRequiredMixin, View):
    """Exporta el reporte de ingresos a Excel."""

    def get(self, request, *args, **kwargs):
        fecha_inicio, fecha_fin = obtener_rango_fechas(request)

        pagos = (
            Pago.objects
            .filter(pagado_en__date__range=(fecha_inicio, fecha_fin))
            .select_related("cita", "cita__cliente", "cita__paquete")
            .order_by("-pagado_en")
        )

        filas = [
            [
                pago.cita.id,
                str(pago.cita.cliente),
                str(pago.cita.paquete),
                pago.metodo.title(),
                pago.monto,
                pago.pagado_en.strftime("%d/%m/%Y"),
            ]
            for pago in pagos
        ]

        return generar_excel_tabla(
            titulo="Reporte de ingresos",
            encabezados=["Cita", "Cliente", "Paquete", "Método", "Monto", "Fecha de pago"],
            filas=filas,
            nombre_archivo="reporte_ingresos",
            columnas_moneda=[4],
        )


class ExportarCitasEstadoPDFView(AdminRequiredMixin, View):
    """Exporta el reporte de citas por estado a PDF."""

    def get(self, request, *args, **kwargs):
        fecha_inicio, fecha_fin = obtener_rango_fechas(request)

        citas_estado = (
            Cita.objects
            .filter(fecha_hora__date__range=(fecha_inicio, fecha_fin))
            .values("estado")
            .annotate(total=Count("id"))
            .order_by("estado")
        )

        filas = [[item["estado"], item["total"]] for item in citas_estado]

        return generar_pdf_tabla(
            titulo="Reporte de citas por estado",
            subtitulo=f"Periodo: {fecha_inicio:%d/%m/%Y} - {fecha_fin:%d/%m/%Y}",
            encabezados=["Estado", "Cantidad de citas"],
            filas=filas,
            nombre_archivo="reporte_citas_estado",
        )


class ExportarCitasEstadoExcelView(AdminRequiredMixin, View):
    """Exporta el reporte de citas por estado a Excel."""

    def get(self, request, *args, **kwargs):
        fecha_inicio, fecha_fin = obtener_rango_fechas(request)

        citas_estado = (
            Cita.objects
            .filter(fecha_hora__date__range=(fecha_inicio, fecha_fin))
            .values("estado")
            .annotate(total=Count("id"))
            .order_by("estado")
        )

        filas = [[item["estado"], item["total"]] for item in citas_estado]

        return generar_excel_tabla(
            titulo="Reporte de citas por estado",
            encabezados=["Estado", "Cantidad de citas"],
            filas=filas,
            nombre_archivo="reporte_citas_estado",
        )


class ExportarServiciosTopPDFView(AdminRequiredMixin, View):
    """Exporta el reporte de paquetes más solicitados a PDF."""

    def get(self, request, *args, **kwargs):
        fecha_inicio, fecha_fin = obtener_rango_fechas(request, dias_default=30)

        paquetes_top = (
            Cita.objects
            .filter(fecha_hora__date__range=(fecha_inicio, fecha_fin))
            .values("paquete__nombre")
            .annotate(
                total_citas=Count("id"),
                ingresos=Sum("pago__monto", filter=Q(estado=Cita.Estado.TERMINADA)),
            )
            .order_by("-total_citas")[:10]
        )

        filas = [
            [p["paquete__nombre"], p["total_citas"], p["ingresos"] or 0]
            for p in paquetes_top
        ]

        return generar_pdf_tabla(
            titulo="Reporte de paquetes más solicitados",
            subtitulo=f"Periodo: {fecha_inicio:%d/%m/%Y} - {fecha_fin:%d/%m/%Y}",
            encabezados=["Paquete", "Cantidad de citas", "Ingresos generados"],
            filas=filas,
            nombre_archivo="reporte_servicios_top",
        )


class ExportarServiciosTopExcelView(AdminRequiredMixin, View):
    """Exporta el reporte de paquetes más solicitados a Excel."""

    def get(self, request, *args, **kwargs):
        fecha_inicio, fecha_fin = obtener_rango_fechas(request, dias_default=30)

        paquetes_top = (
            Cita.objects
            .filter(fecha_hora__date__range=(fecha_inicio, fecha_fin))
            .values("paquete__nombre")
            .annotate(
                total_citas=Count("id"),
                ingresos=Sum("pago__monto", filter=Q(estado=Cita.Estado.TERMINADA)),
            )
            .order_by("-total_citas")[:10]
        )

        filas = [
            [p["paquete__nombre"], p["total_citas"], p["ingresos"] or 0]
            for p in paquetes_top
        ]

        return generar_excel_tabla(
            titulo="Reporte de paquetes más solicitados",
            encabezados=["Paquete", "Cantidad de citas", "Ingresos generados"],
            filas=filas,
            nombre_archivo="reporte_servicios_top",
            columnas_moneda=[2],
        )


class ExportarTecnicosPDFView(AdminRequiredMixin, View):
    """Exporta el reporte de desempeño de técnicos a PDF."""

    def get(self, request, *args, **kwargs):
        fecha_inicio, fecha_fin = obtener_rango_fechas(request)

        tecnicos = (
            Seguimiento.objects
            .filter(
                estado=Seguimiento.Estado.ENTREGADO,
                actualizado_en__date__range=(fecha_inicio, fecha_fin),
            )
            .annotate(
                duracion=ExpressionWrapper(
                    F("actualizado_en") - F("creado_en"),
                    output_field=DurationField()
                )
            )
            .values("tecnico__first_name", "tecnico__last_name")
            .annotate(
                total_servicios=Count("id"),
                tiempo_promedio=Avg("duracion"),
            )
            .order_by("-total_servicios")
        )

        filas = []
        for tecnico in tecnicos:
            nombre = f'{tecnico["tecnico__first_name"]} {tecnico["tecnico__last_name"]}'
            tiempo = tecnico["tiempo_promedio"]
            filas.append([nombre, tecnico["total_servicios"], str(tiempo) if tiempo else "Sin datos"])

        return generar_pdf_tabla(
            titulo="Reporte de desempeño de técnicos",
            subtitulo=f"Periodo: {fecha_inicio:%d/%m/%Y} - {fecha_fin:%d/%m/%Y}",
            encabezados=["Técnico", "Servicios entregados", "Tiempo promedio"],
            filas=filas,
            nombre_archivo="reporte_tecnicos",
        )


class ExportarTecnicosExcelView(AdminRequiredMixin, View):
    """Exporta el reporte de desempeño de técnicos a Excel."""

    def get(self, request, *args, **kwargs):
        fecha_inicio, fecha_fin = obtener_rango_fechas(request)

        tecnicos = (
            Seguimiento.objects
            .filter(
                estado=Seguimiento.Estado.ENTREGADO,
                actualizado_en__date__range=(fecha_inicio, fecha_fin),
            )
            .annotate(
                duracion=ExpressionWrapper(
                    F("actualizado_en") - F("creado_en"),
                    output_field=DurationField()
                )
            )
            .values("tecnico__first_name", "tecnico__last_name")
            .annotate(
                total_servicios=Count("id"),
                tiempo_promedio=Avg("duracion"),
            )
            .order_by("-total_servicios")
        )

        filas = []
        for tecnico in tecnicos:
            nombre = f'{tecnico["tecnico__first_name"]} {tecnico["tecnico__last_name"]}'
            tiempo = tecnico["tiempo_promedio"]
            filas.append([nombre, tecnico["total_servicios"], str(tiempo) if tiempo else "Sin datos"])

        return generar_excel_tabla(
            titulo="Reporte de desempeño de técnicos",
            encabezados=["Técnico", "Servicios entregados", "Tiempo promedio"],
            filas=filas,
            nombre_archivo="reporte_tecnicos",
        )