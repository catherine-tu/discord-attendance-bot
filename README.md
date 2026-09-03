⏱ ATTENDANCE + MAKEUP POLICY ⏱
Rehearsal Attendance
If you are going to miss rehearsal, arrive late, or leave early, you must use the attendance bot to notify AL & CT within your private channel
Bot Command
!attendance name status date reason

Examples:
!attendance cat absent 2/24 sick
!attendance raymond late 2/24 traffic
!attendance joyce leavingearly 2/24 appointment

Attendance Statuses
Member Commands
Meaning
!attendance
In attendance
!late
Will be late
!leavingearly
Leaving early
CT & AL Commands
Meaning
!excused
Absence made up / excused
!absent
Absent
!neversent
Did not submit makeup recording

Makeup Recording Policy
If you miss rehearsal, you may be required to submit an audio recording for attendance credit.
EXCUSED ABSENCES
Send makeup recordings in your private channels within 3 days of the missed rehearsal (ideally, before the next rehearsal)
Examples:
jobs / interviews
academic conflicts (tests, required events)
sickness
events communicated at least 1 month in advance
UNEXCUSED ABSENCES
Send your recording in the public #absences-makeup channel within 3 days of the missed rehearsal

Consequences for Unexcused Absences
Unexcused absences may result in:
studio cleaning responsibilities
current/future solo consideration being subject to the current Exec Board

Automatic Makeup Reminders 🤖
The attendance bot will automatically:
mark attendance statuses in the sheet
send reminder messages after rehearsal for required makeup recordings
remind members to submit attendance credit within 3 days

Attendance Sheet
You can verify or check your status here:
Fa26 Attendance

Additional Bot Commands
Clear an attendance entry
If you made a mistake:
!clearattendance name date

Example:
!clearattendance cat 2/24

Makeup Completion
Only authorized attendance managers (CT, AL) can mark makeup recordings as completed.
!madeup name date

Example:
!madeup cat 2/24

This changes your status to:
✅ Excused (Sent)

Notes
Anyone may ask clarifying questions about absences if needed.
Please communicate conflicts as early as possible.
The attendance system exists to keep rehearsals fair and organized for everyone.

**Setup:**
venv:
python -m venv venv
macOS / Linux: source venv/bin/activate, or Windows: venv\Scripts\activate
pip install discord.py
pip install gspread oauth2client python-dotenv flask
pip list (should output discord.py, gspread, oauth2client, python-dotenv, Flask)
