import streamlit as st
import numpy as np
import math
import sqlite3
from datetime import datetime

st.set_page_config(page_title="Sebberäknare", page_icon="🤖")
st.title("🤖 Sebberäknare")

# --- Databasfunktioner ---
def init_db():
    conn = sqlite3.connect("sebberaknare.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chatlog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_message(role, content):
    conn = sqlite3.connect("sebberaknare.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chatlog (role, content, timestamp) VALUES (?, ?, ?)",
        (role, content, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def load_history():
    conn = sqlite3.connect("sebberaknare.db")
    cursor = conn.cursor()
    cursor.execute("SELECT role, content, timestamp FROM chatlog ORDER BY id")
    rows = cursor.fetchall()
    conn.close()
    return [{"role": role, "content": f"{content}\n\n*({timestamp[:19]})*"} for role, content, timestamp in rows]

def clear_history():
    conn = sqlite3.connect("sebberaknare.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chatlog")
    conn.commit()
    conn.close()

# Initiera databas
init_db()

# Ladda historik vid första besöket
if "chat_history" not in st.session_state:
    st.session_state.chat_history = load_history()
    st.session_state.minnen = []

# Rensa historik
if st.button("🗑️ Rensa historik"):
    clear_history()
    st.session_state.chat_history = []
    st.rerun()

# Första meddelande om inget finns
if not st.session_state.chat_history:
    första_meddelande = {
        "role": "assistant",
        "content": (
            "Hej! Jag är MatteBot.\n\n"
            "Jag kan räkna, komma ihåg anteckningar, hantera vektorer/matriser.\n\n"
            "**Kommandon:**\n"
            "- `beräkna` eller `vad är` (t.ex. 'beräkna 2 + 2')\n"
            "- `kvadratrot` (t.ex. 'kvadratrot 9')\n"
            "- `kom ihåg ...`, `återkalla`, `minns`\n"
            "- `vektor ...` (t.ex. 'vektor 1,2,3 + 4,5,6')\n"
            "- `matris ...` (t.ex. 'matris 1,2;3,4')\n"
            "- `sluta` eller `avsluta` för att avsluta"
        )
    }
    st.session_state.chat_history.append(första_meddelande)
    save_message("assistant", första_meddelande["content"])

# Funktion för att bearbeta inmatning
def process_input(user_input):
    user_input = user_input.strip().lower()
    minnen = st.session_state.minnen
    svar = ""

    if user_input in ("sluta", "avsluta"):
        st.stop()

    elif "beräkna" in user_input or "vad är" in user_input:
        try:
            expr = user_input.replace("beräkna", "").replace("vad är", "")
            resultat = eval(expr)
            svar = f"Svaret är **{resultat}**"
            minnen.append(f"'beräkna' = {user_input} = {resultat}")
        except Exception as e:
            svar = f"Fel vid beräkning: {e}"

    elif "kvadratrot" in user_input:
        try:
            num = float(user_input.split()[-1])
            resultat = math.sqrt(num)
            svar = f"Kvadratroten är **{resultat}**"
            minnen.append(f"'kvadratrot' = {user_input} = {resultat}")
        except Exception:
            svar = "Kunde inte beräkna kvadratroten."

    elif user_input.startswith("kom ihåg"):
        anteckning = user_input.replace("kom ihåg", "").strip()
        minnen.append(anteckning)
        svar = "Jag har sparat det i mitt minne."

    elif user_input in ("återkalla", "minns"):
        if minnen:
            svar = "Här är vad jag minns:\n" + "\n".join(["- " + note for note in minnen])
        else:
            svar = "(ingenting ännu)"

    elif user_input.startswith("vektor"):
        try:
            s = user_input.replace("vektor", "").strip()
            operator = None
            for op in ["+", "-", "/", "x", "*"]:
                if op in s:
                    operator = op
                    parts = s.split(op)
                    v1 = np.array([float(x.strip()) for x in parts[0].split(",")])
                    v2 = np.array([float(x.strip()) for x in parts[1].split(",")])
                    if len(v1) != len(v2):
                        svar = "Vektorerna måste ha samma dimension."
                    else:
                        if op in ("x", "*"):
                            result = v1 * v2
                        elif op == "+":
                            result = v1 + v2
                        elif op == "-":
                            result = v1 - v2
                        elif op == "/":
                            result = v1 / v2
                        svar = f"`{v1}` {op} `{v2}` = `{result}`"
                        minnen.append(f"'vektor' = {user_input} = {result}")
                    break
            if operator is None:
                v = np.array([float(x.strip()) for x in s.split(",")])
                svar = (
                    f"Din vektor: `{v}`\n"
                    f"- Summa: {np.sum(v)}\n"
                    f"- Medelvärde: {np.mean(v)}\n"
                    f"- Kvadrerade: {np.square(v)}"
                )
                minnen.append(f"'vektor' = {user_input} = {v}")
        except Exception as e:
            svar = f"Ogiltig vektor: {e}"

    elif user_input.startswith("matris"):
        try:
            is_axt = "a x a" in user_input or "a * a" in user_input
            is_add = "a + a" in user_input
            is_sub = "a - a" in user_input

            rest = user_input.replace("matris", "", 1).strip()
            rest = rest.replace("a x a", "").replace("a * a", "").strip()
            rest = rest.replace("a + a", "").replace("a - a", "").strip()

            if rest and any(c.isdigit() for c in rest):
                row_strs = rest.split(";")
                rader = [[float(n) for n in row.split(",")] for row in row_strs]
            else:
                return "Ange matrisvärden, t.ex. `matris 1,2; 3,4`"

            M = np.array(rader)
            M2 = None
            svar = f"Matris:\n```python\n{M}\n```\nMatrisᵀ:\n```python\n{M.T}\n```"
            operation_text = ""

            if is_axt:
                M2 = M @ M.T
                operation_text = "A × Aᵀ"
            elif is_add:
                M2 = M + M
                operation_text = "A + A"
            elif is_sub:
                M2 = M - M
                operation_text = "A - A"
            else:
                M2 = M @ M.T
                operation_text = "A × Aᵀ"

            svar += f"\n {operation_text} =\n```python\n{M2}\n```"
            minnen.append(f"'matris' = {operation_text} med {M} + {M.T} = {M2.tolist()}")
            return svar
        except Exception as e:
            return f"Fel i matrisberäkning: {e}"

    else:
        svar = "Jag kan räkna, komma ihåg anteckningar, hantera vektorer/matriser. Prova t.ex. 'matris a x a 1,2;3,4'"

    return svar

# Visa hela konversationen
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Hantera ny användarinmatning
if user_input := st.chat_input("Vad vill du göra?"):
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    save_message("user", user_input)

    svar = process_input(user_input)
    st.session_state.chat_history.append({"role": "assistant", "content": svar})
    save_message("assistant", svar)

    with st.chat_message("user"):
        st.markdown(user_input)
    with st.chat_message("assistant"):
        st.markdown(svar)
