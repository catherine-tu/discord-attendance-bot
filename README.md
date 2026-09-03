# ⏱ Attendance + Makeup Policy ⏱

## Rehearsal Attendance

If you are going to miss rehearsal, arrive late, or leave early, you must use the attendance bot to notify AL & CT within your private channel.

### Bot Command

```
!attendance name status date reason
```

**Examples:**
```
!attendance cat absent 2/24 sick
!attendance raymond late 2/24 traffic
!attendance joyce leavingearly 2/24 appointment
```

### Attendance Statuses

**Member Commands**

| Command | Meaning |
|---|---|
| `!attendance` | In attendance |
| `!late` | Will be late |
| `!leavingearly` | Leaving early |

**CT & AL Commands**

| Command | Meaning |
|---|---|
| `!excused` | Absence made up / excused |
| `!absent` | Absent |
| `!neversent` | Did not submit makeup recording |

## Makeup Recording Policy

If you miss rehearsal, you may be required to submit an audio recording for attendance credit.

**Excused Absences**
Send makeup recordings in your private channels within 3 days of the missed rehearsal (ideally, before the next rehearsal).

Examples:
- Jobs / interviews
- Academic conflicts (tests, required events)
- Sickness
- Events communicated at least 1 month in advance

**Unexcused Absences**
Send your recording in the public `#absences-makeup` channel within 3 days of the missed rehearsal.

### Consequences for Unexcused Absences

Unexcused absences may result in:
- Studio cleaning responsibilities
- Current/future solo consideration being subject to the current Exec Board

## Automatic Makeup Reminders 🤖

The attendance bot will automatically:
- Mark attendance statuses in the sheet
- Send reminder messages after rehearsal for required makeup recordings
- Remind members to submit attendance credit within 3 days

## Attendance Sheet

You can verify or check your status here: **Fa26 Attendance**

## Additional Bot Commands

**Clear an attendance entry**

If you made a mistake:
```
!clearattendance name date
```

Example:
```
!clearattendance cat 2/24
```

**Makeup Completion**

Only authorized attendance managers (CT, AL) can mark makeup recordings as completed.

```
!madeup name date
```

Example:
```
!madeup cat 2/24
```

This changes your status to: ✅ Excused (Sent)

## Notes

- Anyone may ask clarifying questions about absences if needed.
- Please communicate conflicts as early as possible.
- The attendance system exists to keep rehearsals fair and organized for everyone.

## Setup

**Virtual environment:**
```bash
python -m venv venv
```

Activate it:
- macOS / Linux: `source venv/bin/activate`
- Windows: `venv\Scripts\activate`

**Install dependencies:**
```bash
pip install discord.py
pip install gspread oauth2client python-dotenv flask
```

Verify with `pip list` — should include `discord.py`, `gspread`, `oauth2client`, `python-dotenv`, `Flask`.
