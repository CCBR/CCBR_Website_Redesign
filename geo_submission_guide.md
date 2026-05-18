# CCBR Guide: Submitting Bulk RNA-seq Data to GEO

**Audience:** CCBR bioinformaticians and collaborating scientists  
**Scope:** Bulk RNA-seq submission to NCBI GEO from NIH Biowulf  
**Version:** v1.3 (manager review draft — screenshots pending)

> **📷 To-Do (Next Step):** Screenshots are pending and will be added before final publication. All `[SCREENSHOT: ...]` placeholders mark where they will be inserted.

---

## Table of Contents
1. [What is GEO and Why Do We Submit?](#1-what-is-geo-and-why-do-we-submit)
2. [How GEO Submission Works: The Three-Channel Overview](#2-how-geo-submission-works-the-three-channel-overview)
3. [Before You Begin: Accounts, Tools, and Prerequisites](#3-before-you-begin-accounts-tools-and-prerequisites)
4. [Step 1 — Scope Lock: Define Your Submission](#4-step-1--scope-lock-define-your-submission)
5. [Step 2 — Sample Continuity Audit](#5-step-2--sample-continuity-audit)
6. [Step 3 — Metadata Workbook Assembly](#6-step-3--metadata-workbook-assembly)
7. [Step 4 — File Staging and Payload Preparation](#7-step-4--file-staging-and-payload-preparation)
8. [Step 5 — Transfer Files to GEO via FTP](#8-step-5--transfer-files-to-geo-via-ftp)
9. [Step 6 — Upload the Metadata Workbook via GEO Website](#9-step-6--upload-the-metadata-workbook-via-geo-website)
10. [Step 7 — Validation and Remediation](#10-step-7--validation-and-remediation)
11. [Step 8 — Post-Submission: Accession, Embargo, and Manuscript](#11-step-8--post-submission-accession-embargo-and-manuscript)
12. [Troubleshooting Common Problems](#12-troubleshooting-common-problems)

---

## 1. What is GEO and Why Do We Submit?

[NCBI GEO (Gene Expression Omnibus)](https://www.ncbi.nlm.nih.gov/geo/) is the NIH-hosted public repository for high-throughput genomic data, including RNA-seq experiments. Depositing your data in GEO is a requirement for publication in most journals and a condition of many NIH funding mechanisms.

GEO stores both raw data (FASTQ files) and processed data (count matrices, normalized expression files), along with structured metadata describing how the experiment was designed and performed. After submission, your data is held under embargo until the date you specify — typically until the accompanying manuscript is published or a set release date is reached. Once public, your dataset is freely discoverable and downloadable by any researcher worldwide.

A GEO accession (e.g., `GSExxxxxx`) is assigned once your submission is processed. You will include this accession number in your manuscript's Methods and/or Data Availability sections.

---

## 2. How GEO Submission Works: The Three-Channel Overview

GEO submission for sequencing data involves three distinct actions that must happen in a specific order:

```
1. File Transfer (FTP)           → Raw FASTQ files + processed data file(s)
2. Metadata Upload (GEO website) → Filled-out Excel workbook describing the study and samples
3. GEO Review                    → Automated checks + curator review → Accession issued
```

**Critical rule:** These channels are strictly separate. Your data files are transferred by FTP directly to a private GEO server. Your metadata workbook is uploaded separately through the GEO website, after the file transfer is complete. The metadata workbook is never part of the FTP transfer.

> **[SCREENSHOT: GEO sequencing submission page showing the three-step transfer flow — Step 1: personalized upload space, Step 2: FTP credentials panel, Step 3: upload metadata link]**

The full GEO submission guidance for high-throughput sequencing data is available at the [GEO Sequence Submission Guidelines](https://www.ncbi.nlm.nih.gov/geo/info/seq.html). Read this page before your first submission.

---

## 3. Before You Begin: Accounts, Tools, and Prerequisites

### 3.1 GEO Account
You need an NCBI account linked to your NIH email address. If you do not already have one:
1. Go to [https://www.ncbi.nlm.nih.gov/](https://www.ncbi.nlm.nih.gov/) and sign in with NIH enterprise credentials (eRA Commons or PIV-linked).
2. If your NIH account is not yet linked, follow the NCBI account creation and institutional affiliation instructions.

Your GEO login generates a personalized FTP upload directory (assigned when you begin a submission). This directory is private and unique to your account session — treat it as a credential and do not share or publish it. GEO regularly rotates and changes these credentials, so log-in and look them up each time you begin a new submission.

### 3.2 Tools on Biowulf/Helix
- Use `Helix` as it has been optimized for I/O.
- `lftp`: command-line FTP client for transferring files. Available on Biowulf/Helix.
- `md5sum`: for verifying file integrity. Run via `sbatch`, never on the head node for large payloads.
- `screen`: for running long transfers in a persistent session that survives logout.

### 3.3 What to Collect Before Starting
- Raw FASTQ files for all samples to be submitted (confirm file paths on Biowulf).
- At least one processed data file: for bulk RNA-seq, a gene-level expected counts matrix (e.g., from RENEE/RSEM) is standard.
- Protocol information: library preparation kit, sequencing platform and chemistry, RNA extraction method, any relevant sample handling details.
- A list of all samples, their conditions, and their manuscript-confirmed inclusion status.
- Collaborator availability: you will want to ask the PI or project team to fill-in and/or confirm any details you cannot be confident of using manuscript drafts, your own notes, or the report from the sequencing facility before finalizing the submission.

### 3.4 The GEO Metadata Spreadsheet
GEO provides an Excel Metadata Spreadsheet template for sequencing submissions. Download the current version from the [Submitting high-throughput sequence data to GEO](https://www.ncbi.nlm.nih.gov/geo/info/seq.html#metadata) page.

The spreadsheet has multiple tabs. The most important is the **Metadata** tab, which is where you will do the bulk of your work. Other tabs include **Instructions** (read before filling anything in), **Checksums** (where you paste MD5 checksums for your transferred files), and several example tabs showing filled-out Metadata tabs for different data types (bulk RNA-seq, single-cell, etc.).

The **Metadata** tab itself is divided into four all-caps sections:
- **STUDY** — study-level fields: title, summary, overall design, contributors, and processed data file reference
- **SAMPLES** — one row per sample: tissue, conditions, library details, and FASTQ filenames
- **PROTOCOLS** — free-text protocol rows for both wet-lab steps (growth, extraction, library prep) and dry-lab data processing steps (alignment, trimming, counting, etc.)
- **PAIRED-END EXPERIMENTS** — one row per sample listing all FASTQ files for that sample; for standard paired-end bulk RNA-seq this is two files per row

These sections are described in detail in Step 3 of this guide.

> **[SCREENSHOT: GEO metadata spreadsheet template download page]**

---

## 4. Step 1 — Scope Lock: Define Your Submission

Before opening any spreadsheet or staging any files, resolve three questions:

**1. What repository is appropriate?**  
Most RNA-seq studies go to GEO. However, if your raw FASTQ files contain data from human subjects and are subject to restricted access (e.g., protected health information, dbGaP-required studies), the raw files may need to go to [dbGaP](https://www.ncbi.nlm.nih.gov/gap/) instead, with only the processed counts file deposited in GEO. Clarify this with your PI, collaborators, and/or the funding program officer before proceeding.

**2. What is your sample universe?**  
Define clearly: how many samples are being submitted? Are any samples in your analysis excluded from the manuscript? Any sample that is excluded from the manuscript should generally also be excluded from the GEO submission, unless otherwise directed by the journal or PI.

**3. What is your target embargo date?**  
The default is typically one year from the submission date, but this can be adjusted. The embargo can be shortened later if the manuscript publishes earlier. It can also be extended later to a maximum of 3 years. Align on the initial embargo date with your PI before submission.

> **💡 Best Practice:** Document these answers in your project notes before moving on. Not everyone keeps detailed project notes by default — but having these three decisions written down will save significant time if you need to revisit the submission later or if a colleague needs to resume the work.

---

## 5. Step 2 — Sample Continuity Audit

One of the most common sources of metadata errors and submission delays is a mismatch between the samples in your raw data, your analysis, and your manuscript. Before filling out any workbook rows, take a moment to reconcile your sample lists.

> **💡 Best Practice:** GEO does not require you to track sample states in any particular format. However, working through this exercise before touching the workbook is one of the most effective ways to prevent errors that are hard to fix once a submission is in progress. The four-state method below is a reliable approach for catching mismatches before they become submission blockers.

Track four states for every sample:

| State | Description |
|---|---|
| **Received** | Sample appears in raw FASTQ universe |
| **QC-passed** | Sample passed quality control during upstream processing |
| **Analysis-included** | Sample is in the final count matrix or analysis output |
| **Manuscript-included** | Sample appears in the published figures and tables |

For each sample that drops out between states, document the reason:
- **Technical exclusion** — sample failed QC (low read count, high duplication, contamination)
- **Analytical exclusion** — sample was intentionally excluded from the analysis design
- **Manuscript/reporting exclusion** — sample was analyzed but not included in the final manuscript scope
- **Metadata mapping defect** — sample ID mismatch between raw files and metadata records

Unresolved mismatches at this stage will cause workbook inconsistencies later. Do not begin workbook assembly until the continuity audit is complete and your collaborator has confirmed the final sample list.

---

## 6. Step 3 — Metadata Workbook Assembly

### 6.1 Overview of the Workbook Structure
The GEO Metadata Spreadsheet is a single Excel file with multiple tabs. Work primarily in the **Metadata** tab. Other tabs serve supporting roles: **Instructions** explains each field (worth reading before your first submission), **Checksums** is where you paste MD5 checksums for your transferred files, and the example tabs show filled-out Metadata tabs for different data types — the bulk RNA-seq example tab is a useful reference.

The **Metadata** tab is divided into four all-caps sections:

- **STUDY** — study-level fields: title, summary, overall design, contributors, and processed data file reference
- **SAMPLES** — one row per sample with individual metadata: tissue/cell type, treatment, growth conditions, library preparation details, and the FASTQ filenames for that sample
- **PROTOCOLS** — free-text rows for both wet-lab protocols (growth/treatment conditions, nucleic acid extraction, library preparation) and dry-lab data processing steps (alignment, trimming, quantification, reference genome used, etc.)
- **PAIRED-END EXPERIMENTS** — one row per sample, listing all FASTQ files associated with that sample. For standard paired-end bulk RNA-seq this is two files per row. For methods with more files per sample (e.g., scRNA-seq), there can be more.

> **[SCREENSHOT: Excel workbook open to the Metadata tab showing the four all-caps sections: STUDY, SAMPLES, PROTOCOLS, and PAIRED-END EXPERIMENTS]**

### 6.2 Filling the STUDY Section
Key fields and common pitfalls:

| Field | Notes |
|---|---|
| **Title** | Descriptive but concise. Will appear as the dataset title on the GEO page. Often, this is the title of the manuscript. |
| **Summary** | 2–5 sentences describing the biological question, system, and what was measured. Write for a public scientific audience. Often, this is a copy of the manuscript Abstract. |
| **Overall design** | Describe the experimental design: sample groups, comparisons, and rationale. This should be filled-in by your collaborators or derived from the Methods in the manuscript. |
| **Contributors** | One row per person. GEO requires a strict name format: `Firstname, I, Lastname` (with a middle initial) or `Firstname, Lastname` (no middle initial). Free-text alternatives will fail validation. |
| **Processed data file** | Enter the exact filename of your processed data file (e.g., `my_project_expected_counts.tsv`). This must match the filename you transfer in Step 4 — exactly, including case and extension. |

> **[SCREENSHOT: STUDY section contributor rows showing correct name format]**

### 6.3 Filling the SAMPLES Section
Each row represents one sample. Key fields:

| Field | Notes |
|---|---|
| **Sample name** | Your internal sample identifier. Must be unique across the submission. |
| **Title** | A human-readable description of the sample (e.g., "PBMC, Donor 1, Drug A, high dose"). |
| **Source name** | Tissue or cell type of origin (e.g., "peripheral blood mononuclear cells", "tumor cell line"). |
| **Organism** | Scientific name (e.g., `Homo sapiens`). |
| **Characteristics** | Use these columns to encode experimental variables such as treatment, dose, time point, cell line, donor ID. Each unique variable gets its own `characteristics` column with a `variable name: value` format. |
| **Molecule** | Must be a GEO dropdown-accepted value. For standard mRNA-seq: use **`polyA RNA`**. Do not use `mRNA` — it will fail GEO validation. |
| **Description** | Optional free text for additional sample context. |
| **Raw file(s)** | List the exact FASTQ filename(s) for this sample. For paired-end data, one file per column. Filenames must match what you transfer in Step 4 exactly. |
| **Processed data file** | Enter the same processed data filename you listed in the STUDY section for each sample row included in that file, which is often all of them. |

> **[SCREENSHOT: SAMPLES section showing several filled rows with characteristics columns and file name columns populated]**

### 6.4 Filling the PROTOCOLS Section
Write concise but complete protocol descriptions for:
- **Growth or treatment conditions** — typically obtained from the manuscript Methods section or provided directly by your collaborator. CCBR analysts rarely have firsthand knowledge of wet-lab protocols.
- **Nucleic acid extraction** — same as above; obtain from your collaborator or the sequencing facility report if not available in a manuscript draft.
- **Library preparation** — same; include the kit name and version if known.
- **Data processing** — this is the analyst's responsibility. At a minimum, include: alignment tool and version, reference genome and annotation version, and how the processed file was generated (e.g., "Gene-level expected counts generated using RSEM via the RENEE pipeline, aligned to GRCh38 with GENCODE v43 annotation").

> **💡 Best Practice:** If a mature manuscript draft is not yet available, send your collaborators a short explicit list of the first three fields above and ask them to fill those in directly. These wet-lab details almost always have to come from the study team, and the PROTOCOLS section cannot be completed without them.

### 6.5 Collaborator Review Loop
Once the workbook is structurally complete:
1. Send a dated draft copy to the PI and any collaborators named as contributors.
2. Ask them to confirm: sample scope (any exclusions?), treatment and condition naming, study description wording, and protocol accuracy.
3. Incorporate their feedback into a new dated version.
4. Do not finalize the workbook until you have explicit written confirmation from the PI.

> **💡 Best Practice:** Save each workbook version with a date in the filename (e.g., `project_geo_metadata_20260505.xlsx`). If corrections are needed after upload, you will re-upload a revised version — dated filenames make it straightforward to track what changed and when.

---

## 7. Step 4 — File Staging and Payload Preparation

### 7.1 What Files to Include
Your FTP transfer payload must contain:
- All raw FASTQ files for all samples in the submission (one or two per sample for single-end or paired-end, respectively)
- At least one processed data file (your count matrix or normalized expression file)

Nothing else should be in the transfer directory. The GEO Metadata spreadsheet, manifests, and any other support files belong in separate folders.

### 7.2 Workspace Layout
Organize your GEO workspace so the transfer directory is unambiguous:

```
geo_<date>/
├── upload/
│   └── <project>_geo_data_<date>/    ← FTP transfer payload ONLY
│       ├── sample1_R1.fastq.gz
│       ├── sample1_R2.fastq.gz
│       ├── ...
│       └── project_expected_counts.tsv
├── metadata/
│   ├── final/                         ← one current workbook at a time
│   └── working/                       ← drafts, support files, legacy versions
├── md5sums/
├── logs/
└── scripts/
```

> **💡 Best Practice:** This folder layout is a recommendation, not a GEO requirement. GEO only requires that you transfer the correct files via FTP and upload a valid metadata workbook. The structure above keeps your transfer payload clearly separated from working files, simplifies troubleshooting, and integrates well with agentic AI assistance (see the companion `copilot-instructions.geo-submission.md`). Note that `/logs/` and `/scripts/` subdirectories are most relevant when using an automated or agentic submission workflow.

### 7.3 FASTQ Staging Strategy: Hardlinks, Not Symlinks
Your raw FASTQ files are likely stored in a central project rawdata directory. Rather than copying them (expensive) or symlinking them (risky for FTP transfers), use **hardlinks**.

Symlinks point to a file path. When `lftp` mirrors a directory with symlinks, it may transfer the symlink itself rather than the file content, resulting in broken files at the destination. Hardlinks are indistinguishable from the original file; the FTP client transfers them correctly.

Create hardlinks for each FASTQ (assuming same filesystem):
```bash
ln /path/to/rawdata/sample1_R1.fastq.gz /path/to/geo_<date>/upload/<payload_dir>/sample1_R1.fastq.gz
```

To verify your files are hardlinks (not symlinks):
- `ls -l` output: entries beginning with `l` are symlinks; all others (including hardlinks) begin with `-`
- Link count column: a count of `2` or greater for a regular file indicates a hardlink exists

> **💡 Best Practice:** GEO does not specify how you stage your FASTQ files, but symlinks are a known source of silent transfer failures — the FTP client may transfer the link pointer rather than the file content. Hardlinks are strongly recommended when source and staging directories are on the same filesystem.

### 7.4 Building the MD5 Manifest
Once the payload directory is finalized, compute checksums for all files. This is a large operation — submit it via Slurm or run it in an `sinteractive` session. Do not run on the head node:

```bash
# Example sbatch wrapper
find /path/to/upload/<payload_dir>/ -type f | sort | xargs md5sum > md5sums/payload_md5s.tsv
```

Count the output lines and confirm it matches your expected file count before proceeding.

> **💡 Best Practice:** Keep the manifest as a permanent record of what was transferred. If filenames change after the manifest was generated (for example, because you renamed or reorganized the payload directory), update only the path text in the manifest file rather than recomputing checksums from scratch — the file content has not changed, only the path label has. This avoids an expensive re-hash of potentially hundreds of large FASTQ files.

---

## 8. Step 5 — Transfer Files to GEO via FTP

### 8.1 Start from the GEO Website
Before opening a terminal, log in to GEO and navigate to the [GEO File Transfer Protocol (FTP)](https://www.ncbi.nlm.nih.gov/geo/info/submissionftp.html) page. GEO will present you with a personalized upload directory and temporary FTP credentials in Step 2 of this page. These credentials are session-specific.

> **[SCREENSHOT: GEO sequencing submission page, Step 2 panel showing the FTP host, username, and password fields — password obscured]**

Write down (or copy):
- FTP host: `ftp-private.ncbi.nlm.nih.gov`
- Username: `geoftp`
- Password: provided on-page (do not save this to any script or document)
- Your personalized upload directory path: provided on-page (do not share or publish this)

Note: Password and personalized upload directory credentials are rotated by GEO regularly per their security procedures. So, check this page at the start of every new submission to get up-to-date credentials.

### 8.2 Run the Transfer from Biowulf (Helix)
For large transfers, use **Helix** (NIH's I/O-optimized data transfer node), _not_ **Biowulf**. Also, do not execute transfer from VS Code terminal. Use `ssh` in your local Terminal:

```bash
# SSH to Helix from your NIH Mac terminal
ssh helix.nih.gov

# Start a persistent screen session so the transfer survives logout
screen -S geo_transfer

# Open an lftp session — enter password interactively to avoid saving it in history
lftp -u geoftp ftp-private.ncbi.nlm.nih.gov

# Navigate to your personalized upload space
cd uploads/<your_personalized_geo_directory>/

# Mirror your local payload directory up to GEO (recursive upload)
mirror -R /data/CCBR/projects/<project>/geo_<date>/upload/<payload_dir>/

# Verify the remote file count after transfer completes
ls -la | wc -l
```

For large studies (hundreds of FASTQ files), this transfer may run for many hours. The `screen` session keeps it running after you log off. Reconnect with `screen -r geo_transfer` to check progress.

> **[SCREENSHOT: Terminal showing lftp session in progress with file transfer output]**

### 8.3 Verify the Transfer Before Proceeding
Before uploading the metadata workbook, confirm the transfer is complete:
- Remote file count matches expected payload count (use `ls -la | wc -l` in the lftp session).
- Spot-check a few filenames to confirm correct staging — verify sample names and extensions match your payload manifest.

Do not upload the metadata workbook until this verification passes.

---

## 9. Step 6 — Upload the Metadata Workbook via GEO Website

After the file transfer is verified complete, return to the GEO website.

Navigate to the metadata upload step ([Step 3 on the GEO File Transfer Protocol (FTP) page](https://www.ncbi.nlm.nih.gov/geo/info/submissionftp.html)). Upload your final metadata workbook (`.xlsx` format).

> **[SCREENSHOT: GEO website Step 3 — "Upload Metadata" section showing the file chooser for the Excel workbook]**

GEO will run automated validation checks on the workbook immediately after upload. Watch for any error messages on the page or in the confirmation email. Common errors are covered in Step 7, below. You will be required to re-upload metadata until it passes initial automated validation.

Once the workbook is accepted, GEO will begin automated file integrity and format checks on your transferred data files. This process typically takes a few hours to one business day for studies with hundreds of files.

---

## 10. Step 7 — Validation and Remediation

### 10.1 What GEO Checks Automatically
GEO's automated checks verify:
- Workbook format and required field completeness
- Controlled vocabulary compliance (e.g., molecule type, organism)
- Filename consistency between the workbook and uploaded files
- File integrity (checksums, format detection)

You will receive an email notification if any check fails.

### 10.2 Common Validation Errors and How to Fix Them

**Contributor name format rejected**
- GEO enforces a specific format: `Firstname, I, Lastname` or `Firstname, Lastname`.
- Fix: open the STUDY section of the Metadata tab and normalize all contributor rows. Re-upload the corrected workbook.

**Molecule value not accepted**
- GEO validates this field against a controlled vocabulary list. The value `mRNA` is not accepted.
- Fix: replace with `polyA RNA` for standard poly-A selected mRNA-seq libraries. Use drop-down menus on fields in Metadata Spreadsheet to select valid terms. Consult the [GEO sequencing guidelines](https://www.ncbi.nlm.nih.gov/geo/info/seq.html) for the full accepted vocabulary.

**Processed data filename mismatch**
- The filename you entered in the STUDY and/or SAMPLES sections of the Metadata tab does not exactly match the file you transferred.
- Fix: open the workbook and align the filename cell(s) to match the uploaded file exactly — character for character, including case and extension.

**Raw FASTQ filename mismatch**
- Fix: same approach — verify the filenames in the SAMPLES section of the Metadata tab match the actual uploaded filenames exactly.

**Sample name mismatch**
- Fix: same approach — verify the sample names in the SAMPLES section match the sample names in the processed file(s) (e.g. raw counts) exactly.

### 10.3 Applying Fixes
When correcting errors:
- Make only the targeted changes needed to resolve the flagged issues.
- Before re-uploading, review the workbook for structural completeness (all required sections populated, no malformed identifiers) and semantic consistency (filenames exact, controlled vocabulary used, sample IDs correct).
- Re-upload the corrected workbook with a new date in the filename.
- Document what you changed and why.

### 10.4 Timeline Expectations
- Automated file/metadata checks: minutes to a few hours after workbook upload.
- GEO curator review (if triggered): up to 5 business days.
- Accession issuance: typically within 1–3 business days for clean submissions.

---

## 11. Step 8 — Post-Submission: Accession, Embargo, and Manuscript

### 11.1 You Have an Accession
When GEO issues your accession, you will receive an email containing:
- Your GEO accession number (format: `GSExxxxxx`)
- The public URL for the dataset (accessible only to you while the dataset is under embargo)
- Your embargo end date

Record these in your project documentation immediately.

**Generating a Reviewer Token:** The reviewer token is not included in the accession email — you must generate it as a separate step. Log in to GEO and navigate to your accession URL (the page is visible only to you during the embargo period). On that page, find and click the "Generate Reviewer Token" link. The token will be displayed on the page and also sent to you in a separate email. Keep this token safe; it grants read access to your embargoed dataset without making it publicly available.

### 11.2 Notify Collaborators
Send the PI and all listed contributors:
- The accession number and public URL
- The embargo date
- The reviewer token and instructions for sharing it with journal editor and peer reviewers
- How to cite the accession in the manuscript (see below)

### 11.3 Citing the Accession in the Manuscript
Include the accession number in both or either of these two places:
1. **Methods section** — in the data generation or bioinformatics subsection, mention that raw and processed data are deposited in GEO under accession `GSExxxxxx`.
2. **Data Availability statement** — explicitly state the accession and URL.

Example phrasing: *"RNA-seq data have been deposited in NCBI GEO under accession number GSExxxxxx (https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSExxxxxx)."*

### 11.4 Sharing the Reviewer Token
Peer reviewers who need to access the data during the embargo period can do so using the reviewer token. The token + URL allows browsing and downloading without making the dataset public. Typically:
- Include the token in your journal submission alongside the accession number, often in a letter to the editor that accompanies the manuscript.
- Share the token only with the journal editorial system or named reviewers.
- The token is not a public link; treat it with the same care as login credentials.

### 11.5 The Embargo and Early Release
Your embargo date is the date GEO will automatically make your dataset public. The default is typically set at the time of submission (e.g., one year out).

You can request an **early release** at any time if:
- Your manuscript is accepted or published before the embargo date.
- Your funding program requires earlier release.

To request early release, log in to GEO with the submitting account and follow the release instructions on your submission record page, or contact GEO directly at [geo@ncbi.nlm.nih.gov](mailto:geo@ncbi.nlm.nih.gov).

You can also **extend the embargo** if your manuscript timeline changes — for example, due to extended reviewer response rounds or re-submission to multiple journals. To extend, log in to your GEO submission record and update the embargo date directly on the page. GEO permits extensions up to a maximum of 3 years from the initial submission date. If you need an extension beyond that limit, contact GEO at [geo@ncbi.nlm.nih.gov](mailto:geo@ncbi.nlm.nih.gov).

---

## 12. Troubleshooting Common Problems

**Transfer stalls or disconnects mid-way**
- Reconnect to your `screen` session on Helix: `screen -r geo_transfer`
- In the `lftp` session, re-run the `mirror -R` command. `lftp` will skip already-transferred files and resume with remaining ones.
- If the session has ended, start a new `lftp` session, navigate to the same upload subfolder, and re-run `mirror -R`. Do not create a new subfolder.

**Symlinks transferred as broken files**
- This happens when the FTP payload was staged with symlinks instead of hardlinks.
- Delete the affected files from the remote, convert symlinks to hardlinks locally (see Step 4.3), and re-transfer only the affected files.

**Workbook rejected with unclear error message**
- Download the GEO metadata template again from the [GEO sequence submission page](https://www.ncbi.nlm.nih.gov/geo/info/seq.html#metadata) and compare your workbook structure to the template.
- Check that no extra worksheets or columns were introduced accidentally.
- Check that all controlled-vocabulary fields (molecule, library strategy, library source, library selection, platform) use values from the GEO-provided dropdown lists.

**Transfer appears complete but GEO reports missing files**
- Verify that your FASTQ filenames in the SAMPLES section of the Metadata tab match the uploaded filenames exactly (not just visually — copy-paste from an `ls` listing to be sure).
- Check that paired-end files are split into separate columns correctly.

**GEO does not respond after metadata upload**
- The automated checks can take longer for very large datasets. Wait at least 24 hours before following up.
- Check your spam folder for GEO notification emails.
- Contact GEO support at [geo@ncbi.nlm.nih.gov](mailto:geo@ncbi.nlm.nih.gov) if no response after 2 business days.

---

*For questions about this guide, contact the CCBR bioinformatics team.*

*To submit feedback or flag a change, reach out to the guide maintainer before the next review cycle.*

*Companion resource: `copilot-instructions.geo-submission.md` — use this alongside an AI coding assistant to structure and verify each step of your submission.*
