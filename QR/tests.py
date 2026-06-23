from datetime import timedelta

from django.test import Client, TestCase
from django.utils import timezone

from .models import (
    Cylinder_Inward_Details,
    Cylinder_Outward_Details,
    Cylinder_Store,
    Cylinder_Type_Master,
    DEFAULT_CYLINDER_TYPES,
    Gas_Cylinder_Vendors_Master,
)
from .views import build_cylinder_analytics


class CylinderTypeSeedDataTests(TestCase):
    def test_default_cylinder_types_are_seeded(self):
        seeded_types = set(
            Cylinder_Type_Master.objects.filter(
                cylinder_gas_type__in=DEFAULT_CYLINDER_TYPES
            ).values_list("cylinder_gas_type", flat=True)
        )

        self.assertEqual(seeded_types, set(DEFAULT_CYLINDER_TYPES))


class CylinderAnalyticsTests(TestCase):
    def setUp(self):
        self.vendor = Gas_Cylinder_Vendors_Master.objects.create(
            gas_cylinder_vendor_name="Analytics Vendor"
        )
        self.type = Cylinder_Type_Master.objects.get(cylinder_gas_type="Oxygen")
        self.inward = Cylinder_Inward_Details.objects.create(
            cylinder_po_no="PO-1",
            cylinder_po_Date="2026-06-01",
            cylinder_GRN_no="GRN-1",
            cylinder_GRN_Date="2026-06-01",
            cylinder_Invoice_DC_no="INV-1",
            cylinder_description="Analytics stock",
        )
        now = timezone.now()
        Cylinder_Store.objects.create(
            cylinder_sl_r_qr_no="CM-AVAILABLE",
            cylinder_vendor_name=self.vendor,
            cylinder_gas_type=self.type,
            cylinder_scanned_r_submitted_by="tester",
            cylinder_Inward=True,
            cylinder_Inward_Date=now - timedelta(hours=3),
            cylinder_stocked_in=True,
            cylinder_stocked_in_Date=now - timedelta(hours=1),
            Cylinder_Inward_Table=self.inward,
        )
        Cylinder_Store.objects.create(
            cylinder_sl_r_qr_no="CM-PENDING-IN",
            cylinder_vendor_name=self.vendor,
            cylinder_gas_type=self.type,
            cylinder_scanned_r_submitted_by="tester",
            cylinder_Inward=True,
            cylinder_Inward_Date=now,
            Cylinder_Inward_Table=self.inward,
        )
        Cylinder_Store.objects.create(
            cylinder_sl_r_qr_no="CM-PENDING-OUT",
            cylinder_vendor_name=self.vendor,
            cylinder_gas_type=self.type,
            cylinder_scanned_r_submitted_by="tester",
            cylinder_Inward=True,
            cylinder_Inward_Date=now - timedelta(days=1),
            cylinder_stocked_in=True,
            cylinder_stocked_in_Date=now - timedelta(days=1, hours=-1),
            cylinder_Outward=True,
            cylinder_Outward_Date=now,
            Cylinder_Inward_Table=self.inward,
        )

    def test_build_cylinder_analytics_returns_stock_summary_and_charts(self):
        analytics = build_cylinder_analytics()

        self.assertEqual(analytics["summary"]["total_cylinders"], 3)
        self.assertEqual(analytics["summary"]["available_stock"], 1)
        self.assertEqual(analytics["summary"]["pending_inward"], 1)
        self.assertEqual(analytics["summary"]["pending_outward"], 1)
        self.assertEqual(analytics["summary"]["risk_count"], 2)
        self.assertEqual(analytics["summary"]["avg_stock_in_hours"], 1.5)
        self.assertIn("Oxygen", analytics["charts"]["stock_by_type"]["labels"])
        self.assertIn("Analytics Vendor", analytics["charts"]["vendor_mix"]["labels"])
        self.assertTrue(analytics["charts"]["movement"]["labels"])


class CylinderWorkflowTests(TestCase):
    def setUp(self):
        self.client = Client(HTTP_HOST="127.0.0.1")
        session = self.client.session
        session["Login_id"] = "tester"
        session["auth_session_started_at"] = int(timezone.now().timestamp())
        session["auth_last_activity"] = int(timezone.now().timestamp())
        session.save()
        self.vendor = Gas_Cylinder_Vendors_Master.objects.create(
            gas_cylinder_vendor_name="Workflow Vendor"
        )
        self.type = Cylinder_Type_Master.objects.get(cylinder_gas_type="Nitrogen")
        self.inward = Cylinder_Inward_Details.objects.create(
            cylinder_po_no="PO-2",
            cylinder_po_Date="2026-06-02",
            cylinder_GRN_no="GRN-2",
            cylinder_GRN_Date="2026-06-02",
            cylinder_Invoice_DC_no="INV-2",
            cylinder_description="Workflow stock",
        )

    def test_stock_in_updates_only_pending_inward_cylinders(self):
        cylinder = Cylinder_Store.objects.create(
            cylinder_sl_r_qr_no="CM-STOCK-IN",
            cylinder_vendor_name=self.vendor,
            cylinder_gas_type=self.type,
            cylinder_scanned_r_submitted_by="tester",
            cylinder_Inward=True,
            cylinder_Inward_Date=timezone.now(),
            Cylinder_Inward_Table=self.inward,
        )

        response = self.client.post(
            "/QR/Cylinder-Stocking-In",
            {"selectedinward[]": [str(cylinder.cylinder_db_id)]},
            secure=True,
        )

        self.assertEqual(response.status_code, 200)
        cylinder.refresh_from_db()
        self.assertTrue(cylinder.cylinder_stocked_in)
        self.assertIsNotNone(cylinder.cylinder_stocked_in_Date)

    def test_stock_out_requires_return_dc_and_pending_outward_state(self):
        cylinder = Cylinder_Store.objects.create(
            cylinder_sl_r_qr_no="CM-STOCK-OUT",
            cylinder_vendor_name=self.vendor,
            cylinder_gas_type=self.type,
            cylinder_scanned_r_submitted_by="tester",
            cylinder_Inward=True,
            cylinder_Inward_Date=timezone.now() - timedelta(days=1),
            cylinder_stocked_in=True,
            cylinder_stocked_in_Date=timezone.now() - timedelta(hours=3),
            cylinder_Outward=True,
            cylinder_Outward_Date=timezone.now() - timedelta(hours=1),
            Cylinder_Inward_Table=self.inward,
        )

        missing_dc_response = self.client.post(
            "/QR/Cylinder-Stocking-Out",
            {"outwardSelected[]": [str(cylinder.cylinder_db_id)]},
            secure=True,
        )
        self.assertEqual(missing_dc_response.status_code, 400)

        response = self.client.post(
            "/QR/Cylinder-Stocking-Out",
            {
                "outwardSelected[]": [str(cylinder.cylinder_db_id)],
                "return_dc_no": "RDC-1",
                "return_remarks": "Returned",
            },
            secure=True,
        )

        self.assertEqual(response.status_code, 200)
        cylinder.refresh_from_db()
        self.assertTrue(cylinder.cylinder_stock_out)
        self.assertEqual(cylinder.Cylinder_Outward_Table.cylinder_return_DC, "RDC-1")
        self.assertTrue(Cylinder_Outward_Details.objects.filter(cylinder_return_DC="RDC-1").exists())
