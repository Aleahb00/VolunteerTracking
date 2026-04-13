from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import Disaster, Donations, Volunteer


class DashboardSmokeTests(TestCase):
	def setUp(self):
		today = date.today()
		self.disaster = Disaster.objects.create(
			name="Test Disaster",
			number="DR-0001",
			type="Flood",
			category="Category A",
			size="Medium",
			declaration_date=today - timedelta(days=10),
			completion_date=today + timedelta(days=30),
			start_date=today - timedelta(days=7),
			end_date=today + timedelta(days=20),
			location="Test County",
			process_step="Open",
			applicant="Applicant",
			goal=100000,
			active=True,
		)

		self.other_disaster = Disaster.objects.create(
			name="Other Disaster",
			number="DR-0002",
			type="Wind",
			category="Category B",
			size="Small",
			declaration_date=today - timedelta(days=5),
			completion_date=today + timedelta(days=60),
			start_date=today - timedelta(days=3),
			end_date=today + timedelta(days=40),
			location="Other County",
			process_step="Open",
			applicant="Other Applicant",
			goal=50000,
			active=True,
		)

		self.volunteer = Volunteer.objects.create(
			name="Volunteer One",
			contact_method="email",
			email="volunteer@example.com",
			date_of_work=today,
			total_hours=4,
			location_volunteered="Test County",
			work_desc="Debris cleanup",
			skilled_worker="no",
			disaster=self.disaster,
		)

		self.donation = Donations.objects.create(
			name="Donation One",
			contact_method="email",
			email="donation@example.com",
			date_of_donation=today,
			total_hours=2,
			location_donated="Test County",
			work_desc="Supply donation",
			donation_type="material",
			material_type="Lumber",
			disaster=self.disaster,
		)

	def test_general_dashboard_loads(self):
		response = self.client.get(reverse("general_dashboard"))
		self.assertEqual(response.status_code, 200)

	def test_admin_dashboard_loads(self):
		response = self.client.get(reverse("admin_dashboard"))
		self.assertEqual(response.status_code, 200)

	def test_general_volunteer_delete_and_restore(self):
		self.client.post(reverse("delete_volunteer_general", args=[self.volunteer.id]))
		self.volunteer.refresh_from_db()
		self.assertIsNotNone(self.volunteer.deleted)

		self.client.post(reverse("restore_volunteer_general", args=[self.volunteer.id]))
		self.volunteer.refresh_from_db()
		self.assertIsNone(self.volunteer.deleted)

	def test_admin_donation_delete_and_restore(self):
		self.client.post(reverse("delete_donation", args=[self.donation.id]))
		self.donation.refresh_from_db()
		self.assertIsNotNone(self.donation.deleted)

		self.client.post(reverse("restore_donation", args=[self.donation.id]))
		self.donation.refresh_from_db()
		self.assertIsNone(self.donation.deleted)

	def test_general_volunteer_permanent_delete(self):
		self.client.post(reverse("delete_volunteer_general", args=[self.volunteer.id]))
		self.client.post(reverse("permanent_delete_volunteer_general", args=[self.volunteer.id]))
		self.assertFalse(Volunteer.all_objects.filter(id=self.volunteer.id).exists())

	def test_toggle_volunteer_flag_sets_and_clears_manual_reason(self):
		response = self.client.post(reverse("toggle_flagged_status", args=[self.volunteer.id]))
		self.assertEqual(response.status_code, 200)
		self.volunteer.refresh_from_db()
		self.assertTrue(self.volunteer.flagged)
		self.assertEqual(self.volunteer.flagged_reason, ["manually flagged"])

		response = self.client.post(reverse("toggle_flagged_status", args=[self.volunteer.id]))
		self.assertEqual(response.status_code, 200)
		self.volunteer.refresh_from_db()
		self.assertFalse(self.volunteer.flagged)
		self.assertEqual(self.volunteer.flagged_reason, [])

	def test_toggle_donation_flag_sets_and_clears_manual_reason(self):
		response = self.client.post(reverse("toggle_donation_flagged_status", args=[self.donation.id]))
		self.assertEqual(response.status_code, 200)
		self.donation.refresh_from_db()
		self.assertTrue(self.donation.flagged)
		self.assertEqual(self.donation.flagged_reason, ["manually flagged"])

		response = self.client.post(reverse("toggle_donation_flagged_status", args=[self.donation.id]))
		self.assertEqual(response.status_code, 200)
		self.donation.refresh_from_db()
		self.assertFalse(self.donation.flagged)
		self.assertEqual(self.donation.flagged_reason, [])

	def test_close_disaster_marks_inactive_and_redirects(self):
		response = self.client.post(reverse("close_disaster", args=[self.disaster.id]))
		self.assertEqual(response.status_code, 302)
		self.disaster.refresh_from_db()
		self.assertFalse(self.disaster.active)

	def test_update_hourly_rate_for_active_disaster(self):
		response = self.client.post(
			reverse("update_hourly_rate", args=[self.disaster.id]),
			{"hourly_rate": "35.50", "skilled_hourly_rate": "52.25"},
		)
		self.assertEqual(response.status_code, 200)
		self.disaster.refresh_from_db()
		self.assertEqual(self.disaster.hourly_rate, Decimal("35.50"))
		self.assertEqual(self.disaster.skilled_hourly_rate, Decimal("52.25"))

	def test_update_hourly_rate_rejected_for_closed_disaster(self):
		self.disaster.active = False
		self.disaster.save(update_fields=["active"])
		old_hourly = Decimal(str(self.disaster.hourly_rate))

		response = self.client.post(
			reverse("update_hourly_rate", args=[self.disaster.id]),
			{"hourly_rate": "99.99"},
		)
		self.assertEqual(response.status_code, 400)
		self.disaster.refresh_from_db()
		self.assertEqual(Decimal(str(self.disaster.hourly_rate)), old_hourly)

	def test_assign_submission_clears_invalid_location_flag(self):
		self.volunteer.disaster = None
		self.volunteer.flagged = True
		self.volunteer.flagged_reason = [Volunteer.FLAG_INVALID_LOCATION]
		self.volunteer.save(update_fields=["disaster", "flagged", "flagged_reason"])

		response = self.client.post(
			reverse("assign_submission_view", args=["volunteer", self.volunteer.id]),
			{"disaster_id": self.other_disaster.id},
		)
		self.assertEqual(response.status_code, 200)
		self.volunteer.refresh_from_db()
		self.assertEqual(self.volunteer.disaster_id, self.other_disaster.id)
		self.assertFalse(self.volunteer.flagged)

	def test_assign_submission_keeps_non_location_flags(self):
		self.donation.flagged = True
		self.donation.flagged_reason = ["manually flagged"]
		self.donation.save(update_fields=["flagged", "flagged_reason"])

		response = self.client.post(
			reverse("assign_submission_view", args=["donation", self.donation.id]),
			{"disaster_id": self.other_disaster.id},
		)
		self.assertEqual(response.status_code, 200)
		self.donation.refresh_from_db()
		self.assertEqual(self.donation.disaster_id, self.other_disaster.id)
		self.assertTrue(self.donation.flagged)
