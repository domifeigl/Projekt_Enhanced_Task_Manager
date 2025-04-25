import mysql.connector
import pytest

def get_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1111",
        database="my_task_manager"
    )
    return connection

def create_table(connection, test_mode=False):
    table_name = "ukoly_test" if test_mode else "ukoly"
    cursor = connection.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            Id INT AUTO_INCREMENT PRIMARY KEY,
            Nazev VARCHAR(300) NOT NULL,
            Popis VARCHAR(300) NOT NULL,
            Stav ENUM('Nezahájeno', 'Hotovo', 'Probíhá')NOT NULL DEFAULT 'Nezahájeno',
            Datum_vytvoreni DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    connection.commit()
    cursor.close()

def pridat_ukol(connection, Nazev, Popis, test_mode=False):
    if not Nazev:
        print("Název úkolu nemůže být prázdný.")
        return
    
    table_name = "ukoly_test" if test_mode else "ukoly"
    cursor = connection.cursor()
    cursor.execute(f"INSERT INTO {table_name} (Nazev, Popis) VALUES (%s, %s)", (Nazev, Popis))
    connection.commit()
    print(f"Úkol {Nazev} byl přidán do tabulky `{table_name}`.")
    cursor.close()

def zobrazit_ukoly(connection, test_mode=False):
    table_name = "ukoly_test" if test_mode else "ukoly"
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM {table_name}")
    ukoly = cursor.fetchall()
    print("\n Seznam úkolů:")
    for ukol in ukoly:
        print(f"[{ukol['Id']}] {ukol['Nazev']}\n {ukol['Popis']}\n Stav: {ukol['Stav']}\n")
    cursor.close()
    return ukoly

def aktualizovat_ukol(connection, ukol_id, novy_stav, test_mode=False):
    table_name = "ukoly_test" if test_mode else "ukoly"
    if novy_stav not in ['Nezahájeno', 'Hotovo', 'Probíhá']:
        print("Neplatný stav.")
        return
    cursor = connection.cursor()
    cursor.execute(f"UPDATE {table_name}  SET stav = %s WHERE id = %s", (novy_stav, ukol_id,))
    connection.commit()
    cursor.close()
    print(f"Stav úkolu {ukol_id} byl aktualizován.")

def odstranit_ukol(connection, ukol_id, test_mode=False):
    table_name = "ukoly_test" if test_mode else "ukoly"
    cursor = connection.cursor()
    cursor.execute(f"DELETE FROM {table_name} WHERE id = %s", (ukol_id,))
    connection.commit()
    cursor.close()
    print(f"Úkol číslo {ukol_id} byl smazán z `{table_name}`.")


@pytest.fixture(scope="module")
def connection():
    connection = get_connection()
    create_table(connection, test_mode=True)
    yield connection

    cursor = connection.cursor()
    try:
        cursor.execute("DROP TABLE IF EXISTS ukoly_test")
        connection.commit()
    except mysql.connector.Error as e:
        print(f"Testovací tabulku se nepodařilo smazat: {e}")
    cursor.close()
    connection.close()

def test_pridat_ukol(connection):
    pridat_ukol(connection, "Test Ukol", "Test Popis Ukolu", test_mode=True)
    ukoly = zobrazit_ukoly(connection, test_mode=True)
    print("\n Data v testovací databázi po přidání úkolu:")
    print(f"ID: {ukoly[0]['Id']}, Název: {ukoly[0]['Nazev']}, Popis: {ukoly[0]['Popis']}, Stav: {ukoly[0]['Stav']}")
    assert ukoly[0]["Nazev"] == "Test Ukol"
    assert ukoly[0]["Popis"] == "Test Popis Ukolu"

def test_pridat_neuplny_ukol(connection):
    pridat_ukol(connection, "", "Test Popis Ukolu", test_mode=True)
    ukoly = zobrazit_ukoly(connection, test_mode=True)
    print("\n Přidávám úkol bez názvu:")
    print(f"Výsledek: {ukoly}")
    assert len(ukoly) == 0

def test_aktualizovat_ukol(connection):
    pridat_ukol(connection, "Test Ukol", "Test Popis Ukolu", test_mode=True)
    aktualizovat_ukol(connection, 1, 'Hotovo', test_mode=True)
    ukoly = zobrazit_ukoly(connection, test_mode=True)
    print("\n Data v testovací databázi po přidání úkolu:")
    print(f"ID: {ukoly[0]['Id']}, Název: {ukoly[0]['Nazev']}, Popis: {ukoly[0]['Popis']}, Stav: {ukoly[0]['Stav']}")
    assert ukoly[0]["Stav"] == "Hotovo"

def test_neplatna_aktualizace_ukolu(connection):
    pridat_ukol(connection, "Test Ukol", "Test Popis Ukolu", test_mode=True)
    aktualizovat_ukol(connection, 1, 'Jiny', test_mode=True)
    ukoly = zobrazit_ukoly(connection, test_mode=True)
    assert len(ukoly) > 0
    ukol = ukoly[0]
    print("\n Data v testovací databázi po přidání úkolu:")
    print(f"ID: {ukol['Id']}, Název: {ukol['Nazev']}, Popis: {ukol['Popis']}, Stav: {ukol['Stav']}")
    assert ukol["Stav"] == "Nezahájeno"

def test_odstranit_ukol(connection):
    pridat_ukol(connection, "Test Ukol", "Test Popis Ukolu", test_mode=True)
    odstranit_ukol(connection, 1, test_mode=True)
    odstraneny_ukol = zobrazit_ukoly(connection, test_mode=True)
    assert len(odstraneny_ukol) == 0

def test_odstranit_neexistujici_ukol(connection):
    odstranit_ukol(connection, 4, test_mode=True)
    odstraneny_ukol = zobrazit_ukoly(connection, test_mode=True)
    assert odstraneny_ukol  is not None



TESTS = {
    "1": "test_pridat_ukol",
    "2": "test_pridat_neuplny_ukol",
    "3": "test_aktualizovat_ukol",
    "4": "test_neplatna_aktualizace_ukolu",
    "5": "test_odstranit_ukol",
    "6": "test_odstranit_neexistujici_ukol"
}

if __name__ == "__main__":
    conn = get_connection()
    create_table(conn)
    while True:
        print("\n Enhanced Task Manager")
        print("1. Přidat úkol")
        print("2. Zobrazit úkoly")
        print("3. Aktualizovat úkol")
        print("4. Smazat úkol")
        print("5. Automatizované testy")
        print("6. Konec")

        choice = input("Vyberte možnost: ")

        if choice == "1":
            Nazev = input("Název úkolu: ")
            Popis = input("Popis úkolu: ")
            pridat_ukol(conn, Nazev, Popis)

        elif choice == "2":
            zobrazit_ukoly(conn)

        elif choice == "3":
            ukol_id = input("Zadejte ID úkolu: ")
            novy_stav = input("Zadejte nový stav (Nezahájeno / Probíhá / Hotovo): ")
            aktualizovat_ukol(conn, ukol_id, novy_stav)

        elif choice == "4":
            ukol_id = input("Zadejte ID úkolu, který chcete smazat: ")
            odstranit_ukol(conn, ukol_id)
        
        elif choice == "5":
            print("\n Možnosti testů:")
            for key, value in TESTS.items():
                print(f"{key}️⃣ {value}")
            test_choice = input("Vyber test k provedení: ")
            if test_choice in TESTS:
                pytest.main(["-s", "-v", __file__, "-k", TESTS[test_choice]])
                input("\n Test dokončen. Stiskni Enter pro návrat do menu.")

        elif choice == "6":
            print("Zase příště!")
            break

        else:
            print("Špatná volba. Zkuste to znovu.")