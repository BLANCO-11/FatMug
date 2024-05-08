from datetime import timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db.models import Avg, Sum
from .models import PurchaseOrder, HistoricalPerformance, PurchaseOrder, Vendor
from django.db.models import F, ExpressionWrapper, fields


@receiver(post_save, sender=PurchaseOrder)
def update_vendor_performance_metrics(sender, instance, created, **kwargs):
    if created:
        vendor = instance.vendor

        # Calculate on-time delivery rate
        completed_orders = PurchaseOrder.objects.filter(vendor=vendor, status='completed')
        total_completed_orders = completed_orders.count()
        on_time_deliveries = completed_orders.filter(delivery_date__lte=timezone.now()).count()
        on_time_delivery_rate = on_time_deliveries / total_completed_orders if total_completed_orders > 0 else 0.0

        # Calculate quality rating average
        quality_rating_avg = completed_orders.aggregate(avg_quality_rating=Avg('quality_rating'))['avg_quality_rating'] or 0.0

        # Calculate average response time
        response_times_result = completed_orders.exclude(acknowledgment_date__isnull=True).annotate(
            response_time=ExpressionWrapper(
                F('issue_date') - F('acknowledgment_date'),
                output_field=fields.DurationField()
            )
        ).aggregate(avg_response_time=Avg('response_time'))

        response_times = response_times_result['avg_response_time'] or timedelta(seconds=0)
        
        # Convert the average response time to days
        avg_response_time_seconds = response_times.total_seconds()
        avg_response_time_days = avg_response_time_seconds / (3600 * 24)  # Convert seconds to days

        # If the average response time is less than 1 day, set it to 1 day
        avg_response_time_days = max(avg_response_time_days, 1.0)
        
        # print(avg_response_time_days)
        
        # Calculate fulfillment rate
        fulfilled_orders = completed_orders.exclude(issue_date__isnull=True)
        total_orders = PurchaseOrder.objects.filter(vendor=vendor).count()
        fulfillment_rate = fulfilled_orders.count() / total_orders if total_orders > 0 else 0.0

        # Update the vendor's performance metrics
        vendor.on_time_delivery_rate = on_time_delivery_rate
        vendor.quality_rating_avg = quality_rating_avg
        vendor.average_response_time = avg_response_time_days
        vendor.fulfillment_rate = fulfillment_rate
        vendor.save()



@receiver(post_save, sender=Vendor)
def create_historical_performance(sender, instance, created, **kwargs):
    if created:
        # total_orders_count = PurchaseOrder.objects.filter(vendor=instance).count()
        # completed_orders_count = PurchaseOrder.objects.filter(vendor=instance, status='completed').count()
        # fulfillment_rate = completed_orders_count / total_orders_count if total_orders_count > 0 else 0.0

        HistoricalPerformance.objects.create(
            vendor=instance,
            date=timezone.now(),
            on_time_delivery_rate=0.0,
            quality_rating_avg=0.0,
            average_response_time=0.0,
            fulfillment_rate=0
        )