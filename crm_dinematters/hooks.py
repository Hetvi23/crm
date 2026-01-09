# This is a wrapper hooks file for bench compatibility
# The actual hooks are in 'crm.hooks'
# Import everything from crm.hooks to make it available as crm_dinematters.hooks
from crm.hooks import *

# Override app_name to match the installed app name (crm_dinematters)
# This is necessary for bench to correctly identify the app during installation
app_name = "crm_dinematters"
