from django.urls import path

from .views import (
    DashboardView,
    ReporteIngresosView,
    ReporteCitasEstadoView,
    ReporteServiciosTopView,
    ReporteTecnicosView,
    ExportarIngresosPDFView,
    ExportarIngresosExcelView,
    ExportarCitasEstadoPDFView,
    ExportarCitasEstadoExcelView,
    ExportarServiciosTopPDFView,
    ExportarServiciosTopExcelView,
    ExportarTecnicosPDFView,
    ExportarTecnicosExcelView,
)


app_name = "reportes"


urlpatterns = [
    # Dashboard principal
    path(
        "",
        DashboardView.as_view(),
        name="dashboard"
    ),

    # ==========================
    # Reporte de ingresos
    # ==========================
    path(
        "ingresos/",
        ReporteIngresosView.as_view(),
        name="ingresos"
    ),
    path(
        "ingresos/exportar/pdf/",
        ExportarIngresosPDFView.as_view(),
        name="ingresos_pdf"
    ),
    path(
        "ingresos/exportar/excel/",
        ExportarIngresosExcelView.as_view(),
        name="ingresos_excel"
    ),

    # ==========================
    # Reporte de citas por estado
    # ==========================
    path(
        "citas-estado/",
        ReporteCitasEstadoView.as_view(),
        name="citas_estado"
    ),
    path(
        "citas-estado/exportar/pdf/",
        ExportarCitasEstadoPDFView.as_view(),
        name="citas_estado_pdf"
    ),
    path(
        "citas-estado/exportar/excel/",
        ExportarCitasEstadoExcelView.as_view(),
        name="citas_estado_excel"
    ),

    # ==========================
    # Reporte de servicios más solicitados
    # ==========================
    path(
        "servicios-top/",
        ReporteServiciosTopView.as_view(),
        name="servicios_top"
    ),
    path(
        "servicios-top/exportar/pdf/",
        ExportarServiciosTopPDFView.as_view(),
        name="servicios_top_pdf"
    ),
    path(
        "servicios-top/exportar/excel/",
        ExportarServiciosTopExcelView.as_view(),
        name="servicios_top_excel"
    ),

    # ==========================
    # Reporte de desempeño de técnicos
    # ==========================
    path(
        "tecnicos/",
        ReporteTecnicosView.as_view(),
        name="tecnicos"
    ),
    path(
        "tecnicos/exportar/pdf/",
        ExportarTecnicosPDFView.as_view(),
        name="tecnicos_pdf"
    ),
    path(
        "tecnicos/exportar/excel/",
        ExportarTecnicosExcelView.as_view(),
        name="tecnicos_excel"
    ),
]