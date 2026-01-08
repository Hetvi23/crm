# This is a wrapper package for bench compatibility
# The actual app module is 'crm'
from crm import *

# Explicitly expose version for bench's get_current_version function
__version__ = "1.57.2"
__title__ = "Frappe CRM"
