import sys
import numpy as np
import math

def chatbot():
    print("TaskBot: Hej!")
    print("TaskBot: Jag kan räkna, komma ihåg anteckningar, hantera vektorer/matriser. Skriv 'sluta' eller 'avsluta' för att stänga chatten.")
    print("TaskBot: Använd funktioner som 'beräkna / vad är ( Calculate )', 'kvadratrot (Square Root)', 'kom ihåg (Remember)', 'återkalla / minns (Recall)', 'vektor (Array)', 'matris (Matrix)'.")

    minnen = []

    while True:
        user_input = input("Du: ").strip().lower()

        if user_input in ("sluta", "avsluta"):
            print("TaskBot: Hej då!")
            sys.exit(0)

        elif "beräkna" in user_input or "vad är" in user_input:
            try:
                expr = (user_input
                        .replace("beräkna", "")
                        .replace("vad är", ""))
                resultat = eval(expr)
                svar = f"Svaret är {resultat}"
                print(f"TaskBot: {svar}")

                spara = input("TaskBot: Vill du spara detta i minnet? (Y/N): ").strip().lower()
                if spara == "y":
                    minnen.append(f"'beräkna' = {user_input} = {resultat}")
                    print("TaskBot: Sparat i minnet.")
            except Exception as e:
                print(f"TaskBot: Fel vid beräkning: {e}")

        elif "kvadratrot" in user_input:
            try:
                num = float(user_input.split()[-1])
                resultat = math.sqrt(num)
                svar = f"Kvadratroten är {resultat}"
                print(f"TaskBot: {svar}")

                spara = input("TaskBot: Vill du spara detta i minnet? (Y/N): ").strip().lower()
                if spara == "y":
                    minnen.append(f"'kvadratrot' = {user_input} = {resultat}")
                    print("TaskBot: Sparat i minnet.")
            except Exception:
                print("TaskBot: Kunde inte beräkna kvadratroten.")

        elif user_input.startswith("kom ihåg"):
            anteckning = user_input.replace("kom ihåg", "").strip()
            minnen.append(anteckning)
            print("TaskBot: Jag har sparat det i mitt minne.")

        elif user_input in ("återkalla", "minns"):
            print("TaskBot: Här är vad jag minns:")
            if minnen:
                for note in minnen:
                    print("-", note)
            else:
                print("  (ingenting ännu)")

        elif user_input.startswith("vektor"):
            try:
                s = user_input.replace("vektor", "").strip()
                operator = None

                for op in ["+", "-", "/", "x", "*"]:
                    if op in s:
                        operator = op
                        parts = s.split(op)
                        vec1 = [float(x.strip()) for x in parts[0].split(",") if x.strip()]
                        vec2 = [float(x.strip()) for x in parts[1].split(",") if x.strip()]
                        v1 = np.array(vec1)
                        v2 = np.array(vec2)

                        if len(v1) != len(v2):
                            print("TaskBot: Vektorerna måste ha samma dimension.")
                        else:
                            if op in ("x", "*"):
                                result = v1 * v2
                                print(f"TaskBot: {v1} × {v2} = {result}")
                            elif op == "+":
                                result = v1 + v2
                                print(f"TaskBot: {v1} + {v2} = {result}")
                            elif op == "-":
                                result = v1 - v2
                                print(f"TaskBot: {v1} - {v2} = {result}")
                            elif op == "/":
                                result = v1 / v2
                                print(f"TaskBot: {v1} ÷ {v2} = {result}")

                            spara = input("TaskBot: Vill du spara detta i minnet? (Y/N): ").strip().lower()
                            if spara == "y":
                                minnen.append(f"'vektor' = {user_input} = {result}")
                                print("TaskBot: Sparat i minnet.")
                        break

                if operator is None:
                    siffror = [float(x.strip()) for x in s.split(",") if x.strip()]
                    v = np.array(siffror)
                    print(f"TaskBot: Din vektor: {v}")
                    print(f" - Summa:     {np.sum(v)}")
                    print(f" - Medelvärde:{np.mean(v)}")
                    print(f" - Kvadrerade:{np.square(v)}")

                    spara = input("TaskBot: Vill du spara denna vektor i minnet? (Y/N): ").strip().lower()
                    if spara == "y":
                        minnen.append(f"'vektor' = {user_input} = {v}")
                        print("TaskBot: Sparat i minnet.")
            except Exception as e:
                print("TaskBot: Ogiltig vektor eftersom:", e)

        elif user_input.startswith("matris"):
            try:
                is_axt = "a x a" in user_input or "a × a" in user_input

                rest = user_input.replace("matris", "", 1).strip()
                rest = rest.replace("a x a", "").replace("a × a", "").strip()

                if rest and any(c.isdigit() for c in rest):
                    row_strs = rest.split(";")
                    rader = [[float(n) for n in row.split(",")] for row in row_strs]
                else:
                    print("TaskBot: Ange matris rad för rad, kommaseparerade värden (t.ex. 1,2,3). Tom rad för att avsluta:")
                    rader = []
                    while True:
                        rad = input()
                        if not rad.strip():
                            break
                        rader.append([float(n) for n in rad.strip().split(",")])

                M = np.array(rader)
                print("TaskBot: Matris inläst:")
                print(M)

                if is_axt:
                    M2 = M @ M.T
                    print("\nTaskBot: Resultat av A × Aᵀ:")
                    print(M2)
                    spara = input("TaskBot: Vill du spara detta resultat i minnet? (Y/N): ").strip().lower()
                    if spara == "y":
                        minnen.append(f"'matris' = {rader} =\n{M2}")
                        print("TaskBot: Sparat i minnet.")
                else:
                    print(" - Transponat:")
                    print(M.T)
                    print(" - Matris gånger sig själv:")
                    M2 = M @ M.T
                    print(M2)
                    spara = input("TaskBot: Vill du spara detta resultat i minnet? (Y/N): ").strip().lower()
                    if spara == "y":
                        minnen.append(f"'matris' = {rader} =\n{M2}")
                        print("TaskBot: Sparat i minnet.")
            except Exception as e:
                print("TaskBot: Ogiltig matrisinmatning eftersom:", e)

        else:
            print("TaskBot: Jag kan räkna, komma ihåg anteckningar, hantera vektorer/matriser. Prova 'vektor', 'matris', 'beräkna' eller 'kvadratrot'.")


if __name__ == "__main__":
    chatbot()
