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

class DashboardView(AdminRequiredMixin, TemplateView):
    """
    Dashboard principal del módulo de reportes.
    Muestra estadísticas rápidas del sistema.
    """

    template_name = "reportes/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        hoy = timezone.localdate()

        # Primer día del mes actual
        inicio_mes = hoy.replace(day=1)

        # Calcular ingresos del mes
        ingresos_mes = (
            Pago.objects.filter(
                pagado_en__date__range=(inicio_mes, hoy)
            ).aggregate(
                total=Sum("monto")
            )["total"]
            or 0
        )

        # Contar citas pendientes del día
        citas_pendientes_hoy = Cita.objects.filter(
            fecha_hora__date=hoy,
            estado=Cita.Estado.PENDIENTE
        ).count()

        context["ingresos_mes"] = ingresos_mes
        context["citas_pendientes_hoy"] = citas_pendientes_hoy

        return context
class ReporteIngresosView(AdminRequiredMixin, TemplateView):
    """
    Reporte de ingresos del taller.
    Permite filtrar por fechas y método de pago.
    """

    template_name = "reportes/ingresos.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        fecha_inicio, fecha_fin = obtener_rango_fechas(self.request)

        # Validar rango de fechas
        if fecha_fin < fecha_inicio:
            messages.error(
                self.request,
                "La fecha fin debe ser posterior a la fecha de inicio"
            )

            context["error"] = True
            return context

        metodo = self.request.GET.get("metodo")

        pagos = Pago.objects.filter(
            pagado_en__date__range=(fecha_inicio, fecha_fin)
        )

        # Filtrar por método si se seleccionó uno
        if metodo:
            pagos = pagos.filter(metodo=metodo)

        # Total de ingresos
        total_ingresos = pagos.aggregate(
            total=Sum("monto")
        )["total"] or 0

        # Datos para gráfica de línea (ingresos por día)
        ingresos_por_dia = (
            pagos
            .annotate(dia=TruncDate("pagado_en"))
            .values("dia")
            .annotate(total=Sum("monto"))
            .order_by("dia")
        )

        # Datos para gráfica de pastel (por método)
        ingresos_por_metodo = (
            pagos
            .values("metodo")
            .annotate(total=Sum("monto"))
            .order_by("metodo")
        )

        # Enviar datos al template
        context.update({
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "metodo": metodo,
            "pagos": pagos.select_related(
                "cita",
                "cita__cliente",
                "cita__servicio"
            ),
            "total_ingresos": total_ingresos,
            "ingresos_por_dia": list(ingresos_por_dia),
            "ingresos_por_metodo": list(ingresos_por_metodo),
            "sin_datos": not pagos.exists(),
        })

        return context

class ReporteCitasEstadoView(AdminRequiredMixin, TemplateView):
    """
    Reporte de citas agrupadas por estado.
    """

    template_name = "reportes/citas_estado.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        fecha_inicio, fecha_fin = obtener_rango_fechas(self.request)

        # Validar rango de fechas
        if fecha_fin < fecha_inicio:
            messages.error(
                self.request,
                "La fecha fin debe ser posterior a la fecha de inicio"
            )
            context["error"] = True
            return context

        # Consultar citas en el periodo
        citas = Cita.objects.filter(
            fecha_hora__date__range=(fecha_inicio, fecha_fin)
        )

        # Agrupar por estado
        datos_estado = (
            citas
            .values("estado")
            .annotate(total=Count("id"))
            .order_by("estado")
        )

        total_citas = citas.count()

        resultados = []

        for item in datos_estado:
            porcentaje = 0

            if total_citas > 0:
                porcentaje = (
                    item["total"] * 100
                ) / total_citas

            resultados.append({
                "estado": item["estado"],
                "total": item["total"],
                "porcentaje": round(porcentaje, 2),
            })

        # Calcular tasa de cancelación
        canceladas = citas.filter(
            estado=Cita.Estado.CANCELADA
        ).count()

        tasa_cancelacion = 0

        if total_citas > 0:
            tasa_cancelacion = round(
                (canceladas * 100) / total_citas,
                2
            )

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
    """
    Reporte de los servicios más solicitados.
    """

    template_name = "reportes/servicios_top.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Usar últimos 30 días por defecto
        fecha_inicio, fecha_fin = obtener_rango_fechas(
            self.request,
            dias_default=30
        )

        # Validar rango de fechas
        if fecha_fin < fecha_inicio:
            messages.error(
                self.request,
                "La fecha fin debe ser posterior a la fecha de inicio"
            )
            context["error"] = True
            return context

        # Obtener top 10 servicios por número de citas
        servicios = (
            Cita.objects
            .filter(
                fecha_hora__date__range=(fecha_inicio, fecha_fin)
            )
            .values(
                "servicio_id",
                "servicio__nombre"
            )
            .annotate(
                total_citas=Count("id"),
                ingresos=Sum(
                    "pago__monto",
                    filter=Q(
                    estado=Cita.Estado.TERMINADA
                    )
                )
            )
            .order_by("-total_citas")[:10]
        )

        resultados = []

        for servicio in servicios:
            resultados.append({
                "nombre": servicio["servicio__nombre"],
                "total_citas": servicio["total_citas"],
                "ingresos": servicio["ingresos"] or 0,
            })

        context.update({
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "servicios": resultados,
            "sin_datos": len(resultados) == 0,
        })

        return context
    
class ReporteTecnicosView(AdminRequiredMixin, TemplateView):
    """
    Reporte de desempeño de técnicos.
    """

    template_name = "reportes/tecnicos.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        fecha_inicio, fecha_fin = obtener_rango_fechas(self.request)

        # Validar rango de fechas
        if fecha_fin < fecha_inicio:
            messages.error(
                self.request,
                "La fecha fin debe ser posterior a la fecha de inicio"
            )
            context["error"] = True
            return context

        tecnicos = (
            Seguimiento.objects
            .filter(
                estado=Seguimiento.Estado.ENTREGADO,
                actualizado_en__date__range=(
                    fecha_inicio,
                    fecha_fin
                )
            )
            .annotate(
                duracion=ExpressionWrapper(
                    F("actualizado_en") - F("creado_en"),
                    output_field=DurationField()
                )
            )
            .values(
                "tecnico__first_name",
                "tecnico__last_name"
            )
            .annotate(
                total_servicios=Count("id"),
                tiempo_promedio=Avg("duracion")
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
    """
    Exporta el reporte de ingresos a PDF.
    """

    def get(self, request, *args, **kwargs):
        fecha_inicio, fecha_fin = obtener_rango_fechas(request)

        pagos = (
            Pago.objects
            .filter(
                pagado_en__date__range=(fecha_inicio, fecha_fin)
            )
            .select_related(
                "cita",
                "cita__cliente",
                "cita__servicio",
            )
            .order_by("-pagado_en")
        )

        filas = []

        for pago in pagos:
            filas.append([
                pago.cita.id,
                str(pago.cita.cliente),
                str(pago.cita.servicio),
                pago.metodo.title(),
                pago.monto,
                pago.pagado_en.strftime("%d/%m/%Y"),
            ])

        return generar_pdf_tabla(
            titulo="Reporte de ingresos",
            subtitulo=(
                f"Periodo: {fecha_inicio:%d/%m/%Y} "
                f"- {fecha_fin:%d/%m/%Y}"
            ),
            encabezados=[
                "Cita",
                "Cliente",
                "Servicio",
                "Método",
                "Monto",
                "Fecha de pago",
            ],
            filas=filas,
            nombre_archivo="reporte_ingresos",
        )


class ExportarIngresosExcelView(AdminRequiredMixin, View):
    """
    Exporta el reporte de ingresos a Excel.
    """

    def get(self, request, *args, **kwargs):
        fecha_inicio, fecha_fin = obtener_rango_fechas(request)

        pagos = (
            Pago.objects
            .filter(
                pagado_en__date__range=(fecha_inicio, fecha_fin)
            )
            .select_related(
                "cita",
                "cita__cliente",
                "cita__servicio",
            )
            .order_by("-pagado_en")
        )

        filas = []

        for pago in pagos:
            filas.append([
                pago.cita.id,
                str(pago.cita.cliente),
                str(pago.cita.servicio),
                pago.metodo.title(),
                pago.monto,
                pago.pagado_en.strftime("%d/%m/%Y"),
            ])

        return generar_excel_tabla(
            titulo="Reporte de ingresos",
            encabezados=[
                "Cita",
                "Cliente",
                "Servicio",
                "Método",
                "Monto",
                "Fecha de pago",
            ],
            filas=filas,
            nombre_archivo="reporte_ingresos",
            columnas_moneda=[4],
        )
class ExportarCitasEstadoPDFView(AdminRequiredMixin, View):
    """
    Exporta el reporte de citas por estado a PDF.
    """

    def get(self, request, *args, **kwargs):
        fecha_inicio, fecha_fin = obtener_rango_fechas(request)

        citas_estado = (
            Cita.objects
            .filter(
                fecha_hora__date__range=(fecha_inicio, fecha_fin)
            )
            .values("estado")
            .annotate(total=Count("id"))
            .order_by("estado")
        )

        filas = []

        for item in citas_estado:
            filas.append([
                item["estado"],
                item["total"],
            ])

        return generar_pdf_tabla(
            titulo="Reporte de citas por estado",
            subtitulo=(
                f"Periodo: {fecha_inicio:%d/%m/%Y} "
                f"- {fecha_fin:%d/%m/%Y}"
            ),
            encabezados=[
                "Estado",
                "Cantidad de citas",
            ],
            filas=filas,
            nombre_archivo="reporte_citas_estado",
        )


class ExportarCitasEstadoExcelView(AdminRequiredMixin, View):
    """
    Exporta el reporte de citas por estado a Excel.
    """

    def get(self, request, *args, **kwargs):
        fecha_inicio, fecha_fin = obtener_rango_fechas(request)

        citas_estado = (
            Cita.objects
            .filter(
                fecha_hora__date__range=(fecha_inicio, fecha_fin)
            )
            .values("estado")
            .annotate(total=Count("id"))
            .order_by("estado")
        )

        filas = []

        for item in citas_estado:
            filas.append([
                item["estado"],
                item["total"],
            ])

        return generar_excel_tabla(
            titulo="Reporte de citas por estado",
            encabezados=[
                "Estado",
                "Cantidad de citas",
            ],
            filas=filas,
            nombre_archivo="reporte_citas_estado",
        )
    
class ExportarServiciosTopPDFView(AdminRequiredMixin, View):
    """
    Exporta el reporte de servicios más solicitados a PDF.
    """

    def get(self, request, *args, **kwargs):
        fecha_inicio, fecha_fin = obtener_rango_fechas(
            request,
            dias_default=30
        )

        servicios = (
            Cita.objects
            .filter(
                fecha_hora__date__range=(fecha_inicio, fecha_fin)
            )
            .values("servicio__nombre")
            .annotate(
                total_citas=Count("id"),
                ingresos=Sum(
                    "pago__monto",
                    filter=Q(
                        estado=Cita.Estado.TERMINADA
                    )
                )
            )
            .order_by("-total_citas")[:10]
        )

        filas = []

        for servicio in servicios:
            filas.append([
                servicio["servicio__nombre"],
                servicio["total_citas"],
                servicio["ingresos"] or 0,
            ])

        return generar_pdf_tabla(
            titulo="Reporte de servicios más solicitados",
            subtitulo=(
                f"Periodo: {fecha_inicio:%d/%m/%Y} "
                f"- {fecha_fin:%d/%m/%Y}"
            ),
            encabezados=[
                "Servicio",
                "Cantidad de citas",
                "Ingresos generados",
            ],
            filas=filas,
            nombre_archivo="reporte_servicios_top",
        )
class ExportarServiciosTopExcelView(AdminRequiredMixin, View):
    """
    Exporta el reporte de servicios más solicitados a Excel.
    """

    def get(self, request, *args, **kwargs):
        fecha_inicio, fecha_fin = obtener_rango_fechas(
            request,
            dias_default=30
        )

        servicios = (
            Cita.objects
            .filter(
                fecha_hora__date__range=(fecha_inicio, fecha_fin)
            )
            .values("servicio__nombre")
            .annotate(
                total_citas=Count("id"),
                ingresos=Sum(
                    "pago__monto",
                    filter=Q(
                        estado=Cita.Estado.TERMINADA
                    )
                )
            )
            .order_by("-total_citas")[:10]
        )

        filas = []

        for servicio in servicios:
            filas.append([
                servicio["servicio__nombre"],
                servicio["total_citas"],
                servicio["ingresos"] or 0,
            ])

        return generar_excel_tabla(
            titulo="Reporte de servicios más solicitados",
            encabezados=[
                "Servicio",
                "Cantidad de citas",
                "Ingresos generados",
            ],
            filas=filas,
            nombre_archivo="reporte_servicios_top",
            columnas_moneda=[2],
        )
class ExportarTecnicosPDFView(AdminRequiredMixin, View):
    """
    Exporta el reporte de desempeño de técnicos a PDF.
    """

    def get(self, request, *args, **kwargs):
        fecha_inicio, fecha_fin = obtener_rango_fechas(request)

        tecnicos = (
            Seguimiento.objects
            .filter(
                estado=Seguimiento.Estado.ENTREGADO,
                actualizado_en__date__range=(
                    fecha_inicio,
                    fecha_fin
                )
            )
            .annotate(
                duracion=ExpressionWrapper(
                    F("actualizado_en") - F("creado_en"),
                    output_field=DurationField()
                )
            )
            .values(
                "tecnico__first_name",
                "tecnico__last_name"
            )
            .annotate(
                total_servicios=Count("id"),
                tiempo_promedio=Avg("duracion")
            )
            .order_by("-total_servicios")
        )

        filas = []

        for tecnico in tecnicos:
            nombre = (
                f'{tecnico["tecnico__first_name"]} '
                f'{tecnico["tecnico__last_name"]}'
            )

            tiempo = tecnico["tiempo_promedio"]

            filas.append([
                nombre,
                tecnico["total_servicios"],
                str(tiempo) if tiempo else "Sin datos",
            ])

        return generar_pdf_tabla(
            titulo="Reporte de desempeño de técnicos",
            subtitulo=(
                f"Periodo: {fecha_inicio:%d/%m/%Y} "
                f"- {fecha_fin:%d/%m/%Y}"
            ),
            encabezados=[
                "Técnico",
                "Servicios entregados",
                "Tiempo promedio",
            ],
            filas=filas,
            nombre_archivo="reporte_tecnicos",
        )
class ExportarTecnicosExcelView(AdminRequiredMixin, View):
    """
    Exporta el reporte de desempeño de técnicos a Excel.
    """

    def get(self, request, *args, **kwargs):
        fecha_inicio, fecha_fin = obtener_rango_fechas(request)

        tecnicos = (
            Seguimiento.objects
            .filter(
                estado=Seguimiento.Estado.ENTREGADO,
                actualizado_en__date__range=(
                    fecha_inicio,
                    fecha_fin
                )
            )
            .annotate(
                duracion=ExpressionWrapper(
                    F("actualizado_en") - F("creado_en"),
                    output_field=DurationField()
                )
            )
            .values(
                "tecnico__first_name",
                "tecnico__last_name"
            )
            .annotate(
                total_servicios=Count("id"),
                tiempo_promedio=Avg("duracion")
            )
            .order_by("-total_servicios")
        )

        filas = []

        for tecnico in tecnicos:
            nombre = (
                f'{tecnico["tecnico__first_name"]} '
                f'{tecnico["tecnico__last_name"]}'
            )

            tiempo = tecnico["tiempo_promedio"]

            filas.append([
                nombre,
                tecnico["total_servicios"],
                str(tiempo) if tiempo else "Sin datos",
            ])

        return generar_excel_tabla(
            titulo="Reporte de desempeño de técnicos",
            encabezados=[
                "Técnico",
                "Servicios entregados",
                "Tiempo promedio",
            ],
            filas=filas,
            nombre_archivo="reporte_tecnicos",
        )