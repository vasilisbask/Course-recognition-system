

INVITATION_REFERENCE_SUBJECT = 'Reference Request / Αίτημα για συστατική επιστολή'

INVITATION_REFERENCE_BODY = """
<table width="100%" cellpadding="0" cellspacing="0" style="font-family: Arial, sans-serif; background-color:#f5f5f5; padding:20px;">
  <tr>
    <td align="center">

      <table width="600" cellpadding="0" cellspacing="0" style="background:white; padding:30px; border-radius:6px; color:#222; line-height:1.6;">

        <!-- English Section -->
        <tr>
          <td>
            <h2 style="margin-top:0; color:#1a73e8;">Invitation for Reference Letter</h2>

            <p>Dear Sir or Madam,</p>

            <p>The applicant with the following details:</p>

            <table cellpadding="6" cellspacing="0" style="margin-bottom:15px;">
              <tr>
                <td><strong>First name:</strong></td>
                <td>{name}</td>
              </tr>
              <tr>
                <td><strong>Last name:</strong></td>
                <td>{surname}</td>
              </tr>
            </table>

            <p>
              has submitted an application to the PhD program of the Department<br>
              <strong>{department_en} – {university_en}</strong>
            </p>

            <p>
              under the call entitled:<br>
              <em>{call_title_en}</em>
            </p>

            <p>
              The applicant has indicated you as the contact person for a reference letter.
            </p>

            <p>You may submit your reference letter using the following link:</p>

            <table cellpadding="0" cellspacing="0" style="margin:20px 0;">
              <tr>
                <td align="center" style="background:#1a73e8; padding:12px 22px; border-radius:4px;">
                  <a href="{url}" style="color:white; text-decoration:none; font-weight:bold;">
                    Submit Reference Letter
                  </a>
                </td>
              </tr>
            </table>

          </td>
        </tr>

        <!-- Divider -->
        <tr>
          <td>
            <hr style="margin:30px 0; border:none; border-top:1px solid #ddd;">
          </td>
        </tr>

        <!-- Greek Section -->
        <tr>
          <td>

            <h2 style="margin-top:0; color:#1a73e8;">Πρόσκληση για Συστατική Επιστολή</h2>

            <p>Αγαπητέ Κύριε ή Αγαπητή Κυρία,</p>

            <p>Ο υποψήφιος με τα παρακάτω στοιχεία:</p>

            <table cellpadding="6" cellspacing="0" style="margin-bottom:15px;">
              <tr>
                <td><strong>Όνομα:</strong></td>
                <td>{name}</td>
              </tr>
              <tr>
                <td><strong>Επώνυμο:</strong></td>
                <td>{surname}</td>
              </tr>
            </table>

            <p>
              έχει υποβάλει αίτηση στο πρόγραμμα διδακτορικών σπουδών του Τμήματος<br>
              <strong>{department_gr} – {university_gr}</strong>
            </p>

            <p>
              στην πρόσκληση με τίτλο:<br>
              <em>{call_title_gr}</em>
            </p>

            <p>
              και έχει υποδείξει εσάς ως σημείο επαφής για συστατική επιστολή για την αίτησή του.
            </p>

            <p>Μπορείτε να υποβάλετε τη συστατική επιστολή σας στον παρακάτω σύνδεσμο:</p>

            <table cellpadding="0" cellspacing="0" style="margin:20px 0;">
              <tr>
                <td align="center" style="background:#1a73e8; padding:12px 22px; border-radius:4px;">
                  <a href="{url}" style="color:white; text-decoration:none; font-weight:bold;">
                    Υποβολή Συστατικής Επιστολής
                  </a>
                </td>
              </tr>
            </table>

          </td>
        </tr>

      </table>

    </td>
  </tr>
</table>
"""

REFERENCE_NUMBER_SUBJECT = "Αριθμός Πρωτοκόλλου Αίτησης / Application Reference Number"

REFERENCE_NUMBER_BODY = """
<title>Αριθμός Πρωτοκόλλου Αίτησης / Application Reference Number</title>
</head>

<body style="margin:0; padding:0; font-family: Arial, Helvetica, sans-serif; background-color:#f6f6f6;">

<table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f6f6f6; padding:20px;">
<tr>
<td align="center">

<table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff; border-radius:6px; padding:30px;">

<tr>
<td style="font-size:18px; font-weight:bold; color:#333333;">
Επιβεβαίωση Υποβολής Αίτησης<br>
Application Submission Confirmation
</td>
</tr>

<tr>
<td style="padding-top:20px; font-size:14px; color:#333333; line-height:1.6;">
Αγαπητέ/ή,
</td>
</tr>

<tr>
<td style="padding-top:10px; font-size:14px; color:#333333; line-height:1.6;">
Η αίτησή σας υποβλήθηκε επιτυχώς στο σύστημα.
</td>
</tr>

<tr>
<td style="padding-top:10px; font-size:14px; color:#333333; line-height:1.6;">
Ο <strong>αριθμός πρωτοκόλλου της αίτησής σας</strong> είναι:
</td>
</tr>

<tr>
<td align="center" style="padding:20px 0;">
<span style="font-size:22px; font-weight:bold; color:#2a6edb; letter-spacing:1px;">
{reference_number}
</span>
</td>
</tr>

<tr>
<td style="font-size:14px; color:#333333; line-height:1.6;">
Παρακαλούμε διατηρήστε τον αριθμό αυτό για μελλοντική αναφορά ή επικοινωνία σχετικά με την αίτησή σας.
</td>
</tr>

<tr>
<td style="padding-top:25px; border-top:1px solid #e5e5e5;"></td>
</tr>

<tr>
<td style="padding-top:10px; font-size:14px; color:#333333; line-height:1.6;">
Dear Sir or Madam,
</td>
</tr>

<tr>
<td style="padding-top:10px; font-size:14px; color:#333333; line-height:1.6;">
Your application has been successfully submitted to the system.
</td>
</tr>

<tr>
<td style="padding-top:10px; font-size:14px; color:#333333; line-height:1.6;">
Your <strong>application reference number</strong> is:
</td>
</tr>

<tr>
<td align="center" style="padding:20px 0;">
<span style="font-size:22px; font-weight:bold; color:#2a6edb; letter-spacing:1px;">
{reference_number}
</span>
</td>
</tr>

<tr>
<td style="font-size:14px; color:#333333; line-height:1.6;">
Please keep this number for your records. It may be required for any future correspondence regarding your application.
</td>
</tr>

<tr>
<td style="padding-top:20px; font-size:14px; color:#333333;">
Με εκτίμηση / Kind regards,<br>
Admissions Office
</td>
</tr>

</table>

</td>
</tr>
</table>
"""

INFORM_APPLICATION_TITLE = "Υποβλήθηκε Νέα Αίτηση / New Application Submitted"
INFORM_APPLICATION_BODY = """
<title>New Application Submitted</title>
</head>

<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #222;">

<div style="max-width: 600px; margin: auto; padding: 20px;">

<!-- Greek Section -->
<h2 style="color:#2c3e50;">Υποβλήθηκε Νέα Αίτηση</h2>

<p>
Μια νέα αίτηση υποβλήθηκε επιτυχώς στο σύστημα.
</p>

<p>
<strong>Ονοματεπώνυμο Υποψηφίου:</strong> {applicant_name} <br>
<strong>Email:</strong> {applicant_email} <br>
<strong>Αριθμός Αναφοράς Συστήματος:</strong> {reference_number} <br>
<strong>Τίτλος Πρόσκλησης:</strong> {call_title_gr} <br>

</p>


<hr style="margin-top:30px; margin-bottom:30px;">

<!-- English Section -->
<h2 style="color:#2c3e50;">New Application Submitted</h2>

<p>
A new application has been successfully submitted to the system.
</p>

<p>
<strong>Applicant Name:</strong> {applicant_name} <br>
<strong>Email:</strong> {applicant_email} <br>
<strong>System Reference Number:</strong> {reference_number} <br>
<strong>Call title:</strong> {call_title_en} <br>
</p>


<hr style="margin-top:30px;">

</div>
"""