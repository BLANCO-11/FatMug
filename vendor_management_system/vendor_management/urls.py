from django.urls import path
from . import views

urlpatterns = [
    path('api/vendors/', views.VendorListCreateAPIView.as_view(), name='vendor-list-create'),
    path('api/vendors/<str:vendor_code>/', views.VendorRetrieveUpdateDestroyAPIView.as_view(), name='vendor-detail'),
    path('api/vendors/<str:vendor_code>/performance/', views.VendorPerformanceAPIView.as_view(), name='vendor-performance'),
    # path('addVendor/', views.add_vendor, name='add-vendor'),
   
    path('api/purchase_orders/', views.PurchaseOrderListCreateAPIView.as_view(), name='purchaseorder-list-create'),
    path('api/purchase_orders/<str:vendor_code>', views.PurchaseOrdersByVendorAPIView.as_view(), name='purchaseorder-vendor-list'),
    path('api/purchase_orders/<str:po_number>/', views.PurchaseOrderRetrieveUpdateDestroyAPIView.as_view(), name='purchaseorder-detail'),
   
    path('api/historical_performance/', views.HistoricalPerformanceListCreateAPIView.as_view(), name='historicalperformance-list-create'),
    # path('api/historical_performance/<str:vendor__vendor_code>/', views.HistoricalPerformanceAPIView.as_view(), name='historicalperformance-detail'),

    path('api/purchase_orders/<str:po_number>/acknowledge/', views.acknowledge_purchase_order, name='acknowledge_purchase_order'),
    path('', views.index, name='index')
]
