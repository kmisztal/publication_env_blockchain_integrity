# Podsumowanie Pelnej Macierzy

Wygenerowano: 2026-06-23 19:07:46 +02:00

Dataset ID: `openaq_capitals_2025_h2`

Ten dokument podsumowuje wykonana macierz scenariuszy proof-of-concept. To jest artefakt do przegladu eksperymentu, a nie gotowy tekst manuskryptu.

## Zakres

Pelna zaimplementowana macierz scenariuszy zostala uruchomiona z wlaczona weryfikacja.

- Porownane modele: 4
- Wykonane scenariusze: 24
- Etykiety scenariuszy: 24
- Wyjscia weryfikacji per scenariusz: 24
- Wyjscia ewaluacji per scenariusz: 24

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

| Model | Opis |
| --- | --- |
| A | Konwencjonalne przechowywanie kanonicznych pomiarow |
| B | Audit trail bez powiazania hash-chain |
| C | Audit trail z powiazaniem hash-chain |
| D | Audit trail z hash-chain oraz rekonstrukcja proweniencji i stanu uprawnien |

## Zagregowane Statusy

| Status | Liczba |
| --- | ---: |
| `detected` | 19 |
| `expected_not_detected` | 5 |
| `missed` | 0 |
| `partial` | 0 |
| `unexpected_alert` | 0 |

Znaczenie statusow:

- `detected`: verifier wygenerowal oczekiwany kod alertu dla wstrzyknietego scenariusza.
- `expected_not_detected`: scenariusz celowo lezy poza zakresem detekcji danego modelu.
- `missed`: oczekiwany alert nie zostal wygenerowany.
- `partial`: pojawil sie przynajmniej jeden oczekiwany alert, ale nie wszystkie oczekiwane alerty.
- `unexpected_alert`: pojawil sie alert, mimo ze zaden nie byl oczekiwany.

## Macierz Pokrycia Zagrozen

| Zagrozenie | Model A | Model B | Model C | Model D |
| --- | --- | --- | --- | --- |
| `broken_provenance` |  |  |  | `detected` |
| `fake_record_insertion` | `expected_not_detected` | `detected` | `detected` | `detected` |
| `missing_correction_reason` |  |  |  | `detected` |
| `record_deletion` | `expected_not_detected` | `expected_not_detected` | `detected` | `detected` |
| `replay` | `detected` | `detected` | `detected` | `detected` |
| `revoked_actor_key_usage` |  |  |  | `detected` |
| `timestamp_modification` | `expected_not_detected` | `detected` | `detected` | `detected` |
| `unauthorized_correction` |  |  |  | `detected` |
| `value_modification` | `expected_not_detected` | `detected` | `detected` | `detected` |

Puste pola oznaczaja, ze dany scenariusz nie byl stosowany do tego modelu w obecnej implementacji.

## Odczyt Wedlug Modeli

Model A wykrywa w tej macierzy tylko scenariusz `replay`, poniewaz replay tworzy duplikat identyfikatora rekordu. Model A nie ma audit trail ani informacji hash-chain, ktore pozwalalyby wykryc bezposrednia modyfikacje wartosci, modyfikacje czasu, usuniecie rekordu albo sztuczne wstawienie rekordu.

Model B wykrywa modyfikacje wartosci, modyfikacje czasu, sztuczne wstawienie rekordu i replay dzieki kontrolom integralnosci zdarzen audit trail, takim jak payload hash, event ID albo duplicate ID. W tej implementacji nie wykrywa usuniecia rekordu, poniewaz audit trail nie jest powiazany hash-chain.

Model C wykrywa wszystkie podstawowe scenariusze zaimplementowane dla modeli A-C. Powiazanie hash-chain dodaje mozliwosc wykrywania usuniecia rekordu i naruszenia kolejnosci lancucha przez kontrole previous hash.

Model D wykrywa wszystkie scenariusze Modelu C oraz dodatkowo wykrywa naruszenia proweniencji i uprawnien: broken provenance, unauthorized correction, revoked actor key usage oraz missing correction reason.

## Obserwacje Techniczne

- Przejscie od Modelu A do Modelu D pokazuje wzrost pokrycia zagrozen wraz z dodaniem audit trail, hash-chain oraz mechanizmow proweniencji i uprawnien.
- Status `expected_not_detected` oznacza oczekiwane ograniczenie modelu, a nie blad implementacji.
- Niektore scenariusze generuja dodatkowe alerty strukturalne oprocz alertu oczekiwanego dla danego scenariusza. Na przyklad wstawione zdarzenia moga dodatkowo powodowac `previous_hash_mismatch`. Evaluator oznacza scenariusz jako `detected`, jezeli oczekiwany kod alertu jest obecny.
- Macierz jest scenariuszowa i etykietowa. Nie jest jeszcze statystyczna ewaluacja powtarzanych losowych wstrzykniec.

## Ograniczenia

- Zestaw scenariuszy jest kontrolowany i syntetyczny.
- Kazdy obecnie zaimplementowany scenariusz ma jedna etykiete ground-truth.
- `delayed_synchronization` nie jest jeszcze zaimplementowany.
- False-positive rate, false-negative rate, precision, recall i F1 wymagaja jawnego projektu przypadkow negatywnych, zanim powinny byc raportowane.
- Wyniki oceniaja zachowanie modeli integralnosci, a nie jakosc danych srodowiskowych.
- Dataset OpenAQ jest uzyty jako realistyczne zrodlo rozproszonych danych monitoringu srodowiskowego, a nie jako podstawa do wnioskow srodowiskowych.

## Pytania Do Przegladu

1. Czy rozroznienie `detected` i `expected_not_detected` jest wystarczajaco jasne?
2. Czy puste pola w macierzy powinny pozostac puste, czy w kolejnych wersjach lepiej wpisac `not_applicable`?
3. Czy przed interpretacja manuskryptowa potrzebujemy powtorzen scenariuszy?
4. Czy implementujemy `delayed_synchronization` przed zamknieciem zestawu eksperymentow MVP?
