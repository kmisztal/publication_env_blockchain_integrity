# Podsumowanie Pelnej Macierzy

Wygenerowano: 2026-06-23 19:25:16 +02:00

Dataset ID: `openaq_capitals_2025_h2`

Ten dokument podsumowuje wykonana macierz scenariuszy proof-of-concept. To jest artefakt do przegladu eksperymentu, a nie gotowy tekst manuskryptu.

## Zakres

Pelna zaimplementowana macierz scenariuszy zostala uruchomiona z wlaczona weryfikacja.

- Porownane modele: 4
- Wykonane scenariusze: 25
- Etykiety scenariuszy: 25
- Wyjscia weryfikacji per scenariusz: 25
- Wyjscia ewaluacji per scenariusz: 25

Przebieg:

1. Wygenerowanie kontrolowanych artefaktow tampered.
2. Weryfikacja kazdego artefaktu tampered.
3. Porownanie alertow verifiera z etykietami scenariuszy.
4. Agregacja metryk scenariuszy.
5. Eksport macierzy pokrycia zagrozen.

## Pliki Wyjsciowe

- Metryki scenariuszy: `experiments/outputs/metrics/openaq_capitals_2025_h2_scenario_metrics.csv`
- Macierz pokrycia zagrozen: `experiments/outputs/metrics/openaq_capitals_2025_h2_threat_coverage_matrix.csv`
- Podsumowanie metryk: `experiments/outputs/metrics/openaq_capitals_2025_h2_metrics_summary.json`
- Ewaluacje per scenariusz: `experiments/outputs/metrics/tampered/`
- Raporty weryfikacji i pliki alertow per scenariusz: `experiments/outputs/verification/tampered/`
- Artefakty tampered i etykiety: `experiments/data/tampered/`

## Modele

| Model | Krotki opis | Szerszy opis |
| --- | --- | --- |
| A | Konwencjonalne przechowywanie | Przechowuje kanoniczne rekordy pomiarowe bez zdarzen audit trail, bez hash-chain, bez tozsamosci aktora, bez stanu kluczy i bez rekonstrukcji proweniencji. Verifier moze sprawdzic schemat rekordu i duplikaty identyfikatorow, ale nie ma niezaleznego dowodu integralnosci dla zmienionych albo usunietych wartosci. |
| B | Audit trail | Reprezentuje pomiary jako zdarzenia audit trail z deterministycznymi hashami payloadu i identyfikatorami zdarzen, ale bez laczenia zdarzen przez previous hash. Pozwala wykrywac lokalne zmiany payloadu i duplikaty identyfikatorow, ale nie sprawdza ciaglosci calego strumienia zdarzen. |
| C | Audit trail plus hash-chain | Rozszerza Model B przez powiazanie zdarzen polami `previous_hash` i `block_hash`. Dodaje kontrole ciaglosci sekwencji, dzieki czemu usuniecie, replay insertion i naruszenie lancucha sa wykrywalne przez verifier. |
| D | Hash-chain plus proweniencja i uprawnienia | Rozszerza Model C o identyfikatory aktorow i kluczy, stan uprawnien, rewokacje, korekty, kontrole proweniencji oraz delayed synchronization. Pozwala odroznic zwykle naruszenia strukturalne od naruszen governance/provenance, takich jak unauthorized correction albo revoked key usage. |

## Opisy Scenariuszy

| Scenariusz | Krotki opis |
| --- | --- |
| `value_modification` | Zmienia wartosc pomiaru w rekordzie albo payloadzie zdarzenia. |
| `timestamp_modification` | Zmienia timestamp pomiaru oraz, dla modeli zdarzeniowych, timestamp zdarzenia. |
| `record_deletion` | Usuwa rekord pomiarowy albo zdarzenie pomiarowe z artefaktu. |
| `fake_record_insertion` | Wstawia syntetyczny rekord albo zdarzenie z falszywym identyfikatorem. |
| `replay` | Ponownie wstawia istniejacy rekord albo zdarzenie, tworzac duplikat identyfikatora. |
| `broken_provenance` | Podmienia w Modelu D referencje podpisu/klucza na nieautoryzowany klucz. |
| `unauthorized_correction` | Wstawia zdarzenie korekty podpisane kluczem, ktory istnieje, ale nie ma uprawnienia do korekt. |
| `revoked_actor_key_usage` | Odwoluje bazowy klucz przed pozniejszym zdarzeniem pomiarowym, ktore nadal go uzywa. |
| `missing_correction_reason` | Wstawia zdarzenie korekty bez wymaganego powodu korekty. |
| `delayed_synchronization` | Wstawia zdarzenie synchronizacji, ktore przekracza skonfigurowany maksymalny dopuszczalny czas opoznienia. |

## Zagregowane Statusy

| Status | Liczba |
| --- | ---: |
| `detected` | 20 |
| `expected_not_detected` | 5 |
| `missed` | 0 |
| `partial` | 0 |
| `unexpected_alert` | 0 |

Znaczenie statusow:

- `detected`: verifier wygenerowal oczekiwany kod alertu dla wstrzyknietego scenariusza.
- `expected_not_detected`: scenariusz celowo lezy poza zakresem detekcji danego modelu.
- `not_applicable`: scenariusz nie byl stosowany do danego modelu w obecnej implementacji.
- `missed`: oczekiwany alert nie zostal wygenerowany.
- `partial`: pojawil sie przynajmniej jeden oczekiwany alert, ale nie wszystkie oczekiwane alerty.
- `unexpected_alert`: pojawil sie alert, mimo ze zaden nie byl oczekiwany.

## Macierz Pokrycia Zagrozen

| Zagrozenie | Model A | Model B | Model C | Model D |
| --- | --- | --- | --- | --- |
| `broken_provenance` | `not_applicable` | `not_applicable` | `not_applicable` | `detected` |
| `delayed_synchronization` | `not_applicable` | `not_applicable` | `not_applicable` | `detected` |
| `fake_record_insertion` | `expected_not_detected` | `detected` | `detected` | `detected` |
| `missing_correction_reason` | `not_applicable` | `not_applicable` | `not_applicable` | `detected` |
| `record_deletion` | `expected_not_detected` | `expected_not_detected` | `detected` | `detected` |
| `replay` | `detected` | `detected` | `detected` | `detected` |
| `revoked_actor_key_usage` | `not_applicable` | `not_applicable` | `not_applicable` | `detected` |
| `timestamp_modification` | `expected_not_detected` | `detected` | `detected` | `detected` |
| `unauthorized_correction` | `not_applicable` | `not_applicable` | `not_applicable` | `detected` |
| `value_modification` | `expected_not_detected` | `detected` | `detected` | `detected` |

## Odczyt Wedlug Modeli

Model A wykrywa w tej macierzy tylko scenariusz `replay`, poniewaz replay tworzy duplikat identyfikatora rekordu. Model A nie ma audit trail ani informacji hash-chain, ktore pozwalalyby wykryc bezposrednia modyfikacje wartosci, modyfikacje czasu, usuniecie rekordu albo sztuczne wstawienie rekordu.

Model B wykrywa modyfikacje wartosci, modyfikacje czasu, sztuczne wstawienie rekordu i replay dzieki kontrolom integralnosci zdarzen audit trail, takim jak payload hash, event ID albo duplicate ID. W tej implementacji nie wykrywa usuniecia rekordu, poniewaz audit trail nie jest powiazany hash-chain.

Model C wykrywa wszystkie podstawowe scenariusze zaimplementowane dla modeli A-C. Powiazanie hash-chain dodaje mozliwosc wykrywania usuniecia rekordu i naruszenia kolejnosci lancucha przez kontrole previous hash.

Model D wykrywa wszystkie scenariusze Modelu C oraz dodatkowo wykrywa naruszenia proweniencji, uprawnien, korekt, uzycia odwolanych kluczy oraz opoznionej synchronizacji.

## Obserwacje Techniczne

- Przejscie od Modelu A do Modelu D pokazuje wzrost pokrycia zagrozen wraz z dodaniem audit trail, hash-chain oraz mechanizmow proweniencji i uprawnien.
- Status `expected_not_detected` oznacza oczekiwane ograniczenie modelu, a nie blad implementacji.
- Status `not_applicable` oznacza, ze scenariusz nie nalezy do zakresu danego modelu w obecnej implementacji.
- Niektore scenariusze generuja dodatkowe alerty strukturalne oprocz alertu oczekiwanego dla danego scenariusza. Na przyklad wstawione zdarzenia moga dodatkowo powodowac `previous_hash_mismatch`. Evaluator oznacza scenariusz jako `detected`, jezeli oczekiwany kod alertu jest obecny.
- Macierz jest scenariuszowa i etykietowa. Nie jest jeszcze statystyczna ewaluacja powtarzanych losowych wstrzykniec.

## Co Oznaczaja Powtorzenia Scenariuszy

Przez "powtorzenia scenariuszy" mialem na mysli uruchomienie tego samego zagrozenia wiele razy dla roznych rekordow, stacji, timestampow albo seedow losowych. Obecna macierz uzywa jednego deterministycznego wstrzykniecia dla kazdej pary model/zagrozenie. To wystarcza do reprodukowalnego MVP, ale nie mierzy zmiennosci w zaleznosci od pozycji ataku.

## Ograniczenia

- Zestaw scenariuszy jest kontrolowany i syntetyczny.
- Kazdy obecnie zaimplementowany scenariusz ma jedna etykiete ground-truth.
- False-positive rate, false-negative rate, precision, recall i F1 wymagaja jawnego projektu przypadkow negatywnych, zanim powinny byc raportowane.
- Wyniki oceniaja zachowanie modeli integralnosci, a nie jakosc danych srodowiskowych.
- Dataset OpenAQ jest uzyty jako realistyczne zrodlo rozproszonych danych monitoringu srodowiskowego, a nie jako podstawa do wnioskow srodowiskowych.

## Pytania Do Przegladu

1. Czy przed interpretacja manuskryptowa potrzebujemy powtorzen scenariuszy, czy jedno deterministyczne wstrzykniecie na pare model/zagrozenie wystarcza dla MVP?
2. Czy `not_applicable` powinno zostac dopisane rowniez do starszych smoke-test summaries dla pelnej spojnosci?
3. Czy delayed synchronization zostawiamy tylko w Modelu D, czy definiujemy slabsza wersje takze dla Modeli B-C?
