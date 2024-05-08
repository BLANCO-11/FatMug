from django.shortcuts import render, HttpResponse, redirect
from django.utils import timezone
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from .forms import VendorForm
from .models import Vendor, PurchaseOrder, HistoricalPerformance
from .serializers import VendorSerializer, PurchaseOrderSerializer, HistoricalPerformanceSerializer


def index(request):
    return HttpResponse('Bruh')


class VendorListCreateAPIView(generics.ListCreateAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer

class VendorRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    lookup_field = 'vendor_code'

class VendorPerformanceAPIView(generics.RetrieveAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    lookup_field = 'vendor_code'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        performance_data = {
            'on_time_delivery_rate': instance.on_time_delivery_rate,
            'quality_rating_avg': instance.quality_rating_avg,
            'average_response_time': instance.average_response_time,
            'fulfillment_rate': instance.fulfillment_rate,
        }
        return Response(performance_data)

class PurchaseOrderListCreateAPIView(generics.ListCreateAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    
class PurchaseOrdersByVendorAPIView(generics.ListAPIView):
    serializer_class = PurchaseOrderSerializer

    def get_queryset(self):
        vendor_code = self.kwargs['vendor_code']
        return PurchaseOrder.objects.filter(vendor__vendor_code=vendor_code)

class PurchaseOrderRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    lookup_field = 'po_number'
    

class HistoricalPerformanceListCreateAPIView(generics.ListCreateAPIView):
    queryset = HistoricalPerformance.objects.all()
    serializer_class = HistoricalPerformanceSerializer
    lookup_field = 'vendor__vendor_code'

class HistoricalPerformanceRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = HistoricalPerformance.objects.all()
    serializer_class = HistoricalPerformanceSerializer
    lookup_field = 'vendor__vendor_code'
    
class HistoricalPerformanceAPIView(generics.ListAPIView):
    serializer_class = HistoricalPerformanceSerializer

    def get_queryset(self):
        vendor_code = self.kwargs['vendor__vendor_code']
        return HistoricalPerformance.objects.filter(vendor__vendor_code=vendor_code)



@api_view(['POST'])
def acknowledge_purchase_order(request, po_number):
    try:
        purchase_order = PurchaseOrder.objects.get(po_number=po_number)
    except PurchaseOrder.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if purchase_order.status != 'pending':
        return Response({'error': 'Purchase order has already been acknowledged or canceled'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Update acknowledgment_date
    purchase_order.acknowledgment_date = timezone.now()
    purchase_order.save()

    # Recalculate average_response_time
    vendor = purchase_order.vendor
    orders = PurchaseOrder.objects.filter(vendor=vendor, acknowledgment_date__isnull=False).order_by('acknowledgment_date')
    response_times = [(order.acknowledgment_date - order.issue_date).total_seconds() / (3600 * 24) for order in orders]
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    vendor.average_response_time = avg_response_time
    vendor.save()

    return Response(PurchaseOrderSerializer(purchase_order).data)


# Temp function [ignore this]
# def add_vendor(request):
#     if request.method == 'POST':
#         form = VendorForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('vendor-list')  # Redirect to the list of vendors
#         else:
#             print("error", form.errors)
#     else:
#         form = VendorForm()
#     return render(request, 'vendor_form.html', {'form': form})