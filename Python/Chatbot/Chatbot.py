import sys
import numpy as np
import math
import re

def chatbot():
    print("TaskBot: Hej!")
    print("TaskBot: Jag kan räkna, komma ihåg anteckningar, hantera vektorer/matriser. Skriv 'sluta' eller 'avsluta' för att stänga chatten.")
    print("TaskBot: Använd funktioner som 'beräkna / vad är', 'kvadratrot', 'kom ihåg', 'återkalla / minns', 'vektor', 'matris'.")
    
    minnen = []
    matriser = {}

    while True:
        user_input = input("Du: ").strip().lower()

        # Avsluta
        if user_input in ("sluta", "avsluta"):
            print("TaskBot: Hej då!")
            sys.exit(0)

        # Beräkna uttryck
        elif "beräkna" in user_input or "vad är" in user_input:
            try:
                expr = user_input.replace("beräkna", "").replace("vad är", "")
                resultat = eval(expr)
                print(f"TaskBot: Svaret är {resultat}")
                spara = input("TaskBot: Vill du spara detta i minnet? (Y/N): ").strip().lower()
                if spara == "y":
                    minnen.append(f"{user_input} = {resultat}")
                    print("TaskBot: Sparat i minnet.")
            except Exception as e:
                print(f"TaskBot: Fel vid beräkning: {e}")

        # Kvadratrot
        elif "kvadratrot" in user_input:
            try:
                num = float(user_input.split()[-1])
                resultat = math.sqrt(num)
                print(f"TaskBot: Kvadratroten är {resultat}")
                spara = input("TaskBot: Vill du spara detta i minnet? (Y/N): ").strip().lower()
                if spara == "y":
                    minnen.append(f"{user_input} = {resultat}")
                    print("TaskBot: Sparat i minnet.")
            except:
                print("TaskBot: Kunde inte beräkna kvadratroten.")

        # Kom ihåg anteckningar
        elif user_input.startswith("kom ihåg"):
            anteckning = user_input.replace("kom ihåg", "").strip()
            minnen.append(anteckning)
            print("TaskBot: Jag har sparat det i mitt minne.")

        # Återkalla minnen
        elif user_input in ("återkalla", "minns"):
            print("TaskBot: Här är vad jag minns:")
            if minnen:
                for note in minnen:
                    print("-", note)
            else:
                print("  (ingenting ännu)")

        # Vektor (array)
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
                            elif op == "+":
                                result = v1 + v2
                            elif op == "-":
                                result = v1 - v2
                            elif op == "/":
                                result = v1 / v2
                            print(f"TaskBot: Resultat: {result}")
                        break

                if operator is None:
                    siffror = [float(x.strip()) for x in s.split(",") if x.strip()]
                    v = np.array(siffror)
                    print(f"TaskBot: Din vektor: {v}")
                    print(f" - Summa:     {np.sum(v)}")
                    print(f" - Medelvärde:{np.mean(v)}")
                    print(f" - Kvadrerade:{np.square(v)}")

            except Exception as e:
                print("TaskBot: Ogiltig vektor eftersom:", e)


        # Matris
        elif user_input.startswith("matris"):
            try:
                s = user_input.replace("matris", "", 1).strip()

                # Matrisuttryck, t.ex. "a + a"
                match = re.match(r"([a-z])\s*([\+\-\*@])\s*([a-z])", s)
                if match:
                    a, op, b = match.groups()
                    if a not in matriser or b not in matriser:
                        print("TaskBot: En eller båda matriserna är inte definierade.")
                        continue
                    A = matriser[a]
                    B = matriser[b]

                    if op in ("+", "-") and A.shape != B.shape:
                        print("TaskBot: Matriserna har inte samma dimension.")
                        continue
                    if op in ("*", "@") and A.shape[1] != B.shape[0]:
                        print("TaskBot: Dimensioner för matrisprodukt stämmer inte.")
                        continue

                    if op == "+":
                        result = A + B
                    elif op == "-":
                        result = A - B
                    elif op in ("*", "@"):
                        result = A @ B

                    print("TaskBot: Resultat:")
                    print(result)

                    spara = input("TaskBot: Vill du spara detta i minnet? (Y/N): ").strip().lower()
                    if spara == "y":
                        minnen.append(f"matris {s} = \n{result}")
                        print("TaskBot: Sparat i minnet.")
                    continue

                # Matrisnamn och definition
                assign_match = re.match(r"([a-z])\s*=\s*(.*)", s)
                if assign_match:
                    namn = assign_match.group(1)
                    rest = assign_match.group(2)
                else:
                    namn = None
                    rest = s

                if rest and any(c.isdigit() for c in rest):
                    row_strs = rest.split(";")
                    rader = [[float(n) for n in row.split(",")] for row in row_strs]
                else:
                    print("TaskBot: Ange matris rad för rad (t.ex. 1,2,3). Tom rad för att avsluta:")
                    rader = []
                    while True:
                        rad = input()
                        if not rad.strip():
                            break
                        rader.append([float(n) for n in rad.strip().split(",")])

                M = np.array(rader)
                print("TaskBot: Matris inläst:")
                print(M)

                if namn:
                    matriser[namn] = M
                    print(f"TaskBot: Matrisen sparad som '{namn}'.")

                print(" - Transponat:")
                print(M.T)
                print(" - Matris gånger sig själv:")
                print(M @ M.T)


            except Exception as e:
                print("TaskBot: Ogiltig matrisinmatning:", e)


        # Standard
        else:
            print("TaskBot: Jag kan räkna, komma ihåg anteckningar, hantera vektorer/matriser. Prova 'vektor', 'matris', 'beräkna' eller 'kvadratrot'.")


if __name__ == "__main__":
    chatbot()
