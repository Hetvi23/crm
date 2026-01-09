# This module provides after_migrate hooks for crm_dinematters
# It wraps the original crm hooks and adds default lead statuses

import frappe


def after_migrate():
	"""After migrate hook that safely handles app name mismatch"""
	try:
		# Add default lead statuses using direct database operations
		# We can't use frappe.new_doc() because of app name resolution issues
		# during migration (crm_dinematters vs crm)
		_add_default_lead_statuses_safe()
		
		# Call the original after_migrate hook for FCRM Settings dropdown items
		from crm.fcrm.doctype.fcrm_settings.fcrm_settings import after_migrate as _fcrm_after_migrate
		_fcrm_after_migrate()
	except Exception as e:
		# Log error but don't fail migration
		frappe.log_error(
			title="After Migrate Error",
			message=f"Error in after_migrate hook: {str(e)}"
		)


def _add_default_lead_statuses_safe():
	"""Add default lead statuses using direct database operations to avoid controller loading issues"""
	statuses = {
		"New": {
			"color": "gray",
			"position": 1,
		},
		"Contacted": {
			"color": "orange",
			"position": 2,
		},
		"Nurture": {
			"color": "blue",
			"position": 3,
		},
		"Qualified": {
			"color": "green",
			"position": 4,
		},
		"Unqualified": {
			"color": "red",
			"position": 5,
		},
		"Junk": {
			"color": "purple",
			"position": 6,
		},
	}
	
	# Check if DocType exists in database
	if not frappe.db.exists("DocType", "CRM Lead Status"):
		frappe.log_error(
			title="CRM Lead Status DocType not found",
			message="Cannot add default lead statuses - CRM Lead Status DocType does not exist"
		)
		return
	
	for status, config in statuses.items():
		# Check if status already exists using direct SQL query
		if frappe.db.exists("CRM Lead Status", status):
			continue
		
		try:
			# Use direct database insert to avoid controller loading issues
			frappe.db.sql("""
				INSERT INTO `tabCRM Lead Status` 
				(name, lead_status, color, position, creation, modified, owner, modified_by)
				VALUES (%s, %s, %s, %s, NOW(), NOW(), %s, %s)
			""", (
				status,
				status,
				config["color"],
				config["position"],
				frappe.session.user,
				frappe.session.user
			))
			frappe.db.commit()
		except Exception as e:
			# Log error but continue with other statuses
			frappe.log_error(
				title="Error creating CRM Lead Status",
				message=f"Failed to create lead status '{status}': {str(e)}"
			)
			frappe.db.rollback()
