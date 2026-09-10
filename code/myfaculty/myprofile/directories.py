
# Upload folder for project files 
def project_dir(instance, filename):
    return "projects/{0}/{1}".format(instance.coordinator.user.username, filename)

# Upload folder for leave files 
def leave_dir(instance, filename):
    return "leaves/{0}/{1}".format(instance.applicant.user.username, filename)

# Upload folder for leave files 
def timesheets_dir(instance, filename):
    return "timesheets/{0}/{1}".format(instance.applicant.user.username, filename)

# Upload directory functions for the doctorates app

# Upload folder for CV files
def cv_dir(instance, filename):
    return f"doctorates/applications/{instance.user.username}/files/{filename}"

# Upload folder for doctoral plan files
def doctoral_plan_dir(instance, filename):
    return f"doctorates/applications/{instance.applicant.user.username}/files/{filename}"

# Upload folder for degree files
def degree_dir(instance, filename):   
    return f"doctorates/applications/{instance.applicant.user.username}/files/{instance.type}/{filename}"

# Upload folder for reference letter files
def reference_letter_dir(instance, filename):
    return f"doctorates/applications/{instance.doctorate_application.applicant.user.username}/files/{filename}" 

# Upload folder for invitation document files
def invitation_document_dir(instance, filename):
    return f"doctorates/public/invitation_document/{filename}"

# Upload folder for contract document files
def contract_dir(instance, filename):
    return f"doctorates/applications/{instance.applicant.user.username}/files/{filename}"

# Upload folder for ID document files
def id_dir(instance, filename):
    return f"doctorates/applications/{instance.user.username}/files/{filename}"

# Upload folder for declaration files
def declaration_dir(instance, filename):
    return f"doctorates/applications/{instance.doctorate_application.applicant.user.username}/files/{filename}"

# Upload folder for declaration files
def competency_dir(instance, filename):
    return f"doctorates/applications/{instance.applicant.user.username}/files/{filename}"

# Upload folder for publication pdf files
def pub_dir(instance, filename):
    return f"doctorates/applications/{instance.applicant.user.username}/files/{filename}"

# Upload folder for Phd theses
def phd_dir(instance, filename):
    return f"phdstuds/{instance.thesis.candidate.user.username}/files/{filename}"

# Generic Upload Folder for PhdApps
def phdapp_dir(instance, filename):
    if hasattr(instance, 'application'):
        username = instance.application.applicant.user.username
        idx = instance.application.id
    else:
        username = instance.applicant.user.username
        idx = instance.id
    return f"phdapplications/applicants/{username}/{idx}/files/{filename}"

# Public Folder for PhdApps
def phdapp_public_dir(instance, filename):
    return f"phdapplications/public/files/{filename}"

# Reference Letter Folder for PhdApps
def phdapp_ref_dir(instance, filename):
    return f"phdapplications/refs/{instance.id}/files/{filename}"