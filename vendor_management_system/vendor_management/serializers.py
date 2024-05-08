from rest_framework import serializers
from .models import Vendor, PurchaseOrder, HistoricalPerformance

class VendorCodeField(serializers.CharField):
    def to_internal_value(self, data):
        try:
            return Vendor.objects.get(vendor_code=data)
        except Vendor.DoesNotExist:
            raise serializers.ValidationError(f"Vendor with vendor code '{data}' does not exist.")

class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = '__all__'

class PurchaseOrderSerializer(serializers.ModelSerializer):
    vendor = VendorCodeField()
    
    class Meta:
        model = PurchaseOrder
        fields = '__all__'

class HistoricalPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricalPerformance
        fields = '__all__'
        lookup_field = 'vendor__vendor_code'
