# 🛒 Reseller Discord Bot

Bot για reselling page στο Discord: σύστημα παραγγελιών (tickets), κατάλογος
υπηρεσιών, auto-role & καλωσόρισμα, χειροκίνητη επιβεβαίωση πληρωμής.

## 📁 Δομή

```
reseller-bot/
├── main.py              # Εκκίνηση του bot
├── config.json           # Ρυθμίσεις (products, ρόλοι, κανάλια)
├── requirements.txt
├── .env.example
└── cogs/
    ├── tickets.py         # Σύστημα παραγγελιών
    ├── catalog.py         # /catalog
    ├── welcome.py         # Auto-role + καλωσόρισμα
    └── admin.py           # /settings ... , /product ...
```

## 1️⃣ Δημιουργία του Bot στο Discord

1. Πήγαινε στο https://discord.com/developers/applications
2. **New Application** → δώσε όνομα (π.χ. το όνομα του shop σου)
3. Στο μενού αριστερά πήγαινε **Bot** → **Add Bot**
4. Ενεργοποίησε (Privileged Gateway Intents):
   - ✅ **SERVER MEMBERS INTENT** (χρειάζεται για welcome/autorole)
   - ✅ **MESSAGE CONTENT INTENT**
5. Πάτα **Reset Token** → **Copy** το token (το χρειάζεσαι στο βήμα 3)
   ⚠️ Μην το μοιραστείς με κανέναν — όποιος το έχει, ελέγχει το bot σου.
6. Πήγαινε **OAuth2 → URL Generator**:
   - Scopes: `bot`, `applications.commands`
   - Bot permissions: `Manage Channels`, `Manage Roles`, `Send Messages`,
     `Embed Links`, `Read Message History`, `View Channels`
   - Αντίγραψε το URL που δημιουργείται και άνοιξέ το στον browser για να
     προσκαλέσεις το bot στο server σου.

## 2️⃣ Εγκατάσταση στον υπολογιστή σου

Χρειάζεσαι **Python 3.10+** (κατέβασέ το από python.org αν δεν το έχεις,
και τσέκαρε "Add Python to PATH" στην εγκατάσταση).

```bash
cd reseller-bot
pip install -r requirements.txt
```

Μετά:

1. Αντίγραψε το `.env.example` σε `.env`
2. Άνοιξε το `.env` και βάλε το token σου:
   ```
   DISCORD_TOKEN=το_token_σου_εδω
   ```

## 3️⃣ Εκκίνηση του bot

```bash
python main.py
```

Αν όλα πάνε καλά θα δεις στο τερματικό: `Συνδέθηκε ως <όνομα bot>`.

Για να τρέχει το bot 24/7 χωρίς να έχεις ανοιχτό τον υπολογιστή σου μόνιμα,
θα χρειαστείς κάποιο hosting (π.χ. VPS). Πες μου αν θέλεις προτάσεις — αυτό
είναι ξεχωριστό βήμα από τη σημερινή ρύθμιση.

## 4️⃣ Πρώτες ρυθμίσεις μέσα στο Discord

Μόλις το bot μπει στο server, ως **admin** τρέξε αυτές τις slash εντολές:

| Εντολή | Τι κάνει |
|---|---|
| `/settings staff-role @Staff` | Ορίζει ποιος ρόλος βλέπει/διαχειρίζεται τα tickets |
| `/settings ticket-category ΌνομαΚατηγορίας` | Πού θα δημιουργούνται τα κανάλια παραγγελιών |
| `/settings log-channel #logs` | Κανάλι όπου καταγράφονται tickets/πληρωμές |
| `/settings welcome-channel #welcome` | Κανάλι μηνυμάτων καλωσορίσματος |
| `/settings autorole @Member` | Ρόλος που παίρνουν αυτόματα τα νέα μέλη |
| `/product add name price description` | Προσθέτει υπηρεσία στον κατάλογο |
| `/product remove name` | Αφαιρεί υπηρεσία |
| `/product list` | Λίστα προϊόντων (μόνο για σένα) |
| `/ticket-panel` | Στέλνει το panel με το κουμπί "🛒 Νέα Παραγγελία" |
| `/catalog` | Εμφανίζει τον δημόσιο κατάλογο |

💡 Μπορείς επίσης να επεξεργαστείς απευθείας το `config.json` αν προτιμάς
(πρέπει να κάνεις restart το bot μετά).

## 🔄 Πώς δουλεύει η ροή παραγγελίας

1. Πελάτης βλέπει `/catalog` και βλέπει τις υπηρεσίες/τιμές
2. Πατάει **🛒 Νέα Παραγγελία** στο panel → ανοίγει ιδιωτικό κανάλι μόνο για
   αυτόν + το staff
3. Μέσα στο ticket συμφωνείτε λεπτομέρειες, ο πελάτης πληρώνει χειροκίνητα
   (PayPal/κρύπτο κ.λπ., όπως ορίσεις στο `config.json → payment_methods`)
4. Το staff πατάει **✅ Επιβεβαίωση Πληρωμής** → καταγράφεται στο log κανάλι
5. Όταν τελειώσει η δουλειά, το staff πατάει **🔒 Κλείσιμο Ticket**

## ⚠️ Σημαντικό για ασφάλεια

- Μην ανεβάσεις ποτέ το `.env` (με το token) κάπου δημόσια (π.χ. GitHub).
- Δεν υπάρχει αυτόματη επεξεργασία πληρωμών εδώ — είναι σκόπιμα χειροκίνητο,
  όπως ζήτησες. Να είσαι πάντα προσεκτικός με chargebacks σε PayPal κ.λπ.
