from django.test import TestCase, override_settings
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token

from ..serializers import VendorSerializer, PurchaseOrderSerializer, HistoricalPerformanceSerializer
from ..models import Vendor, PurchaseOrder, HistoricalPerformance
from ..signals import update_vendor_performance_metrics

class SignalTestCase(TestCase):
    
    def test_update_vendor_performance_metrics(self):
        # Create a vendor
        vendor = Vendor.objects.create(name='Test Vendor', vendor_code='TEST123')

        # Create items list with quantities
        items = [{"name": "Item 1", "quantity": 10}, {"name": "Item 2", "quantity": 5}]

        # Calculate total quantity
        total_quantity = sum(item['quantity'] for item in items)

        # Create a completed order with delivery and acknowledgment dates in the past
        purchase_order = PurchaseOrder.objects.create(
            po_number='PO123',
            vendor=vendor,
            order_date=timezone.now(),
            delivery_date=timezone.now() - timezone.timedelta(days=10),  # Ensure delivery_date is in the past
            acknowledgment_date=timezone.now() - timezone.timedelta(days=3),
            items=items,
            quantity=total_quantity,  # Total quantity of items
            status='completed',
            quality_rating=4  # Assuming a quality rating is provided
        )

        # Trigger the signal to update the vendor's performance metrics
        update_vendor_performance_metrics(sender=None, instance=purchase_order, created=True)

        # Check if the vendor's performance metrics are correctly updated
        vendor.refresh_from_db()
        self.assertEqual(vendor.on_time_delivery_rate, 1.0)  # Expecting on_time_delivery_rate to be 1.0
        self.assertEqual(vendor.quality_rating_avg, 4.0)  # Assuming a single quality rating of 4
        self.assertAlmostEqual(vendor.average_response_time, 3.0, places=1)  
        
        # Check if a HistoricalPerformance instance is created for the vendor
        self.assertTrue(HistoricalPerformance.objects.filter(vendor=vendor).exists())

        # Check if the fulfilment_rate in HistoricalPerformance is correctly updated
        completed_orders_count = PurchaseOrder.objects.filter(vendor=vendor, status='completed').count()
        total_orders_count = PurchaseOrder.objects.filter(vendor=vendor).count()    
        
        fulfilment_rate = completed_orders_count / total_orders_count if total_orders_count > 0 else 0.0

        self.assertAlmostEqual(vendor.fulfillment_rate, fulfilment_rate, places=1)
        

class APITest(APITestCase):
    
    def setUp(self):
        self.vendor_data = {
            'name': 'Test Vendor',
            'contact_details': 'Contact Details',
            'address': 'Vendor Address',
            'vendor_code': 'VENDOR010',
            'quality_rating_avg' : '4.0',
        }
        vendorObject = Vendor.objects.create(**self.vendor_data) 
        
        self.purchase_order_data = {
            'po_number': 'PO010',
            'vendor': vendorObject,
            'order_date': '2024-05-08T12:00:00Z',
            'delivery_date': '2024-05-15T12:00:00Z',
            'items': [{'name': 'Item 1', 'quantity': 10}],
            'quantity': 10,
            'status': 'pending',
        }
        self.historical_performance_data = {
            'vendor': vendorObject,
            'date': '2024-05-08T12:00:00Z',
            'on_time_delivery_rate': 0.95,
            'quality_rating_avg': 4.5,
            'average_response_time': 2.5,
            'fulfillment_rate': 0.85,
        }
        
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_vendor_list_retrieve(self):
        url = '/api/vendors/'
        response = self.client.get(url, self.vendor_data, format='json')        
        # print(response.json())
        data = response.json()[0]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['name'], self.vendor_data['name'])

    def test_vendor_retrieve_update_destroy(self):
        vendor_code = Vendor.objects.get_or_create(**self.vendor_data)[0]
        # print("vcode -", vendor[0])
        url = f'/api/vendors/{vendor_code}/'
        response = self.client.get(url)
        data = response.json()
        # print(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['name'], self.vendor_data['name'])

    def test_vendor_performance(self):
        vendor_code = Vendor.objects.get_or_create(**self.vendor_data)[0]
        url = f'/api/vendors/{vendor_code}/performance/'
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['quality_rating_avg'], float(self.vendor_data['quality_rating_avg']))

    def test_purchase_order_list_vendor(self):
        vendor_code = Vendor.objects.get_or_create(**self.vendor_data)[0]        
        url = '/api/purchase_orders/{vendor_code}'
        response = self.client.get(url, self.purchase_order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_purchase_order_retrieve_update_destroy(self):
        purchase_order = PurchaseOrder.objects.create(**self.purchase_order_data)
        url = f'/api/purchase_orders/{purchase_order.po_number}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
