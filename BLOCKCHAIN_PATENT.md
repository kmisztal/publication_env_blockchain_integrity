# Blockchain Patent Background

This file summarizes the blockchain patent material in `resources/` and identifies how the approach can inform the environmental monitoring article.

## Reviewed Resources

1. `resources/US11985227.pdf`
   - United States Patent US 11,985,227 B2.
   - Title: Method and a system for securing data, especially data of biotechnological laboratories.
   - Patent date: May 14, 2024.
   - Inventors listed in the patent: Krzysztof Misztal, Aleksandra Kubica-Misztal, Tomasz Sluzalec.
   - Assignee: DICELLA SP. Z O.O.

2. `resources/Springer_Lecture_Notes_in_Computer_Science.pdf`
   - Article version titled Securing data of biotechnological laboratories using blockchain technology.
   - Describes the laboratory-oriented blockchain approach behind the patent family.

3. `resources/CISIM_presentaion.pdf`
   - Presentation version of the same concept.
   - Useful for quickly identifying architectural elements, block fields, block types, and validation rules.

## Core Patent Idea

The reviewed patent material describes a method and system for securing sensitive laboratory data using a blockchain-based architecture. The central scientific and engineering idea is to preserve data authorship, immutability, access control, and auditability in workflows where records must not be forged, silently modified, deleted, or repudiated.

The system is designed for biotechnological laboratory data, but several ideas are transferable to rural environmental monitoring:

1. Each data record is treated as an authored transaction.
2. Data changes are not silent overwrites; they become traceable blockchain events.
3. User permissions are also represented as blockchain-controlled records.
4. A central server verifies consistency and immutability across subsystem blockchains.
5. Summary blocks reduce verification cost while preserving integrity checking.
6. The architecture supports semi-decentralized operation, which is more practical than fully decentralized blockchain in constrained environments.

## Important Architectural Elements

### Two Blockchain Data Domains

The patent distinguishes between:

1. A blockchain database for information data.
2. A blockchain database for access data, including digital keys and permissions.

For the environmental monitoring paper, this can be adapted as:

1. Environmental measurement integrity chain:
   - sensor reading hash,
   - measurement metadata,
   - sensor identifier,
   - station or gateway identifier,
   - timestamp,
   - correction or validation state.

2. Environmental access and governance chain:
   - operator identities,
   - sensor/station ownership,
   - data submitter permissions,
   - reviewer permissions,
   - correction permissions,
   - publication permissions.

This is useful because rural monitoring systems may involve multiple actors: local operators, municipalities, laboratories, environmental agencies, universities, NGOs, and infrastructure providers.

### Authored Transactions

In the patent approach, a record is connected to the author through a digital signature. A record should be attributable and non-repudiable.

For the environmental paper, the equivalent concept is:

1. A sensor or gateway signs submitted measurements.
2. A human operator signs manual validation, correction, or rejection events.
3. A review service records audit decisions without overwriting the original measurement.

This aligns strongly with clinical data integrity concepts such as attributable records, audit trails, and controlled correction workflows. TODO:CITATION_NEEDED

### Hash Linking and Cryptographic Integrity

The reviewed material uses hash linking between blocks and discusses SHA-3 for block hashes. It also discusses RSA signatures with large keys in the laboratory implementation.

For the environmental paper, the direct transferable principle is not a fixed algorithm choice, but the architectural requirement:

1. Every record or batch has a cryptographic digest.
2. Each new event references prior state through a previous hash.
3. A verification service can recalculate hashes and detect inconsistency.
4. Algorithm choice must be justified from current cryptographic standards. TODO:CITATION_NEEDED

The manuscript should avoid claiming that SHA-3 or RSA-4096 is always the best choice for environmental monitoring unless this is specifically justified. TODO:CITATION_NEEDED

### Genesis Block and Administrative Trust

The patent material defines a genesis block controlled by an administrator. The genesis block starts the chain and establishes initial administrative authority.

Environmental adaptation:

1. A monitoring network genesis record can define the monitoring campaign, responsible institution, sensor inventory, public keys, and governance policy.
2. A rural station or region may have its own genesis configuration.
3. New sensors or operators are added through controlled authorization events.
4. Administrative trust must be explicit, because rural monitoring systems are not necessarily fully decentralized.

### Permission Blocks

The patent material defines user permissions and key insertion/revocation as blockchain events. Presentation material identifies block types including:

1. Genesis block.
2. Insert block.
3. Update block.
4. Insert key.
5. Revoke key.

Environmental adaptation:

1. Insert measurement.
2. Update or correct measurement.
3. Insert sensor key.
4. Revoke sensor key.
5. Insert operator key.
6. Revoke operator key.
7. Approve data publication.
8. Mark data as suspect or invalid.

This provides a concrete way to translate clinical audit trail logic into environmental monitoring.

### Summary Blocks

The patent material introduces summary blocks as checkpoint-like blocks containing hashes of preceding blocks and the hash of the latest summary block. The purpose is to reduce computation time while preserving the ability to verify chain integrity.

This is highly relevant for rural environmental monitoring:

1. Rural stations may have limited computing resources.
2. Sensor gateways may be intermittently connected.
3. Full chain verification on every synchronization may be inefficient.
4. Summary blocks can provide periodic verification checkpoints.

Environmental adaptation:

1. Generate summary blocks per time interval, for example hourly, daily, or per synchronization batch.
2. Include hashes of recent measurement blocks.
3. Include the previous summary hash.
4. Include current active permissions or sensor key status.
5. Use summary blocks to support efficient audit review.

Any performance claims about summary blocks require experiments. TODO:EXPERIMENT_NEEDED

### Semi-Decentralized Architecture

The patent material argues that full decentralization is often unnecessary or impractical for laboratory settings. Instead, it proposes a semi-decentralized setup with subsystem blockchains and a central server that periodically verifies hashes and timestamps.

This is probably the most important concept to reuse in the environmental article.

Environmental adaptation:

1. Each rural monitoring station, sensor gateway, or local authority maintains a local integrity chain.
2. A central verifier stores only hashes, timestamps, and summary evidence.
3. The central verifier periodically checks local chains for corruption or inconsistency.
4. Stations can continue collecting data during connectivity interruptions.
5. Synchronization produces verifiable integrity evidence after reconnection.

This gives the paper a practical architecture that is more credible than a fully public blockchain design for rural monitoring systems.

## Validation and Stability Rules

The reviewed material contains a validation checklist for inserting blocks. Examples include detecting:

1. Missing or invalid genesis block.
2. More than one genesis block.
3. Unexpected previous hash.
4. Timestamp inconsistency.
5. Previous hash mismatch.
6. Invalid proof/hash string condition.
7. Duplicate key insertion.
8. Duplicate key deletion.
9. Deleted genesis key.
10. Unauthorized block insertion because of missing or rejected key.
11. Missing mandatory block fields.

Environmental adaptation:

1. Reject measurements from unknown or revoked sensor keys.
2. Detect sensor records with broken previous-hash links.
3. Detect corrections without authorized operator signatures.
4. Detect timestamp inconsistencies between sensor, gateway, and verifier.
5. Detect duplicate submissions or replayed records.
6. Detect missing mandatory metadata such as location, sensor ID, measurement type, unit, timestamp, and calibration status.
7. Detect unauthorized publication or deletion attempts.

This can become a concrete evaluation scenario in the paper. TODO:EXPERIMENT_NEEDED

## How to Use This Approach in the Article

The article should not simply say that environmental monitoring should use blockchain. The stronger scientific framing is:

1. Environmental monitoring can borrow regulated data integrity patterns from clinical and laboratory systems.
2. The reviewed patent provides an author-owned example of applying blockchain to sensitive laboratory data integrity.
3. The paper can generalize this pattern into an environmental data integrity architecture.
4. The novelty should be the transfer and adaptation to rural environmental monitoring constraints.

Recommended manuscript framing:

1. Present the patent/laboratory approach as author background and conceptual precedent.
2. Identify which elements transfer well:
   - signed transactions,
   - immutable correction trail,
   - access control chain,
   - summary blocks,
   - semi-decentralized verification,
   - central hash verifier,
   - offline/closed-network feasibility.
3. Identify which elements need adaptation:
   - sensor identities instead of laboratory employees,
   - station/gateway keys instead of user-only keys,
   - environmental metadata instead of laboratory notes/results,
   - synchronization after intermittent connectivity,
   - public environmental data publication workflows.
4. Avoid claiming empirical success for environmental monitoring until tested. TODO:EXPERIMENT_NEEDED

## Proposed Environmental Architecture Inspired by the Patent

Working architecture name:

Semi-decentralized environmental integrity chain.

Components:

1. Rural sensor node:
   - collects measurements,
   - signs or forwards measurement events,
   - may have limited computation.

2. Local gateway:
   - batches measurements,
   - creates measurement blocks,
   - stores local chain during connectivity outages,
   - generates summary blocks.

3. Access and governance registry:
   - stores active sensor keys,
   - stores operator/reviewer permissions,
   - records revocations and authorization changes.

4. Central verifier:
   - receives hashes, timestamps, and summaries,
   - periodically verifies local chains,
   - detects mismatches and unauthorized changes,
   - produces audit reports.

5. Off-chain environmental data repository:
   - stores raw or processed measurements,
   - stores larger files or datasets,
   - is verified against blockchain hashes.

6. Audit review interface:
   - shows measurement provenance,
   - shows correction history,
   - shows verification failures,
   - supports reviewer sign-off.

## Possible Research Contribution from This Patent-Inspired Direction

The paper can contribute a structured adaptation of a laboratory blockchain integrity method to rural environmental monitoring.

Candidate contribution statement:

This work proposes a semi-decentralized environmental data integrity architecture inspired by blockchain-based laboratory data security. The architecture separates measurement integrity, permission governance, local station operation, and central hash verification, enabling auditability under rural constraints such as intermittent connectivity, limited computation, and distributed operational responsibility.

This contribution still requires literature support and empirical validation. TODO:CITATION_NEEDED TODO:EXPERIMENT_NEEDED

## Patent-Inspired Hypotheses

H-P1: A semi-decentralized blockchain integrity layer can support environmental data verification while reducing the need for full-chain replication at every rural monitoring node. TODO:EXPERIMENT_NEEDED

H-P2: Summary blocks can reduce verification cost for environmental sensor chains while preserving detection of unauthorized modification. TODO:EXPERIMENT_NEEDED

H-P3: Separating measurement records from access-control records improves auditability of environmental data corrections and publication workflows. TODO:EXPERIMENT_NEEDED

H-P4: A central verifier that stores hashes and timestamps, rather than full raw datasets, is better aligned with rural monitoring infrastructure constraints than full on-chain data storage. TODO:EXPERIMENT_NEEDED

## Boundaries and Cautions

1. The patent is about biotechnological laboratory data, not environmental monitoring.
2. The article must clearly state that the environmental architecture is an adaptation, not a direct validation.
3. The patent does not provide environmental datasets or environmental experimental results.
4. Any claim about rural performance, storage cost, network resilience, or tamper detection must be tested. TODO:EXPERIMENT_NEEDED
5. Any cryptographic algorithm recommendation must be supported by current standards or literature. TODO:CITATION_NEEDED
6. The patent should be used as background and design inspiration, not as a substitute for environmental monitoring related work.

## Immediate Next Steps

1. Add this patent-inspired architecture to `notes/paper_context.md` as a design direction.
2. Add a decision that the manuscript will use a semi-decentralized integrity architecture inspired by the patent.
3. Create a future system architecture figure showing:
   - rural sensor nodes,
   - local gateways,
   - local blockchains,
   - summary blocks,
   - access governance chain,
   - central hash verifier,
   - off-chain environmental repository.
4. Define a small future experiment using simulated sensor tampering and summary-block verification. TODO:EXPERIMENT_NEEDED
5. Decide whether the patent itself should be cited in the manuscript bibliography or mentioned only as author background.
