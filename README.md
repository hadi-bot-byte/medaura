# MEDAURA - A Cloud-Based Offline Medication Reminder System.
> **Medaura** is a cloud based, offline-first medication reminder application that enables patients reliably track and manage their medication schedules even in areas with poor or no internet connectivity.
> **Medaura's** system combines **distributed systems principles** and **cloud computing** to ensure a fault-tolerant, scalable, and acessible healthcare and availability solution for patients across the African continent.
# Overview
In the different regions across the African continent, millions of people depend on daily medication to manage chronic illnesses such as **diabetes**, **kidney disease**, **asthma**, **Heart disease**. However, a large portion of these patients struggle to maintain a consistent medication schedule due to forgetfulness, complex dose prescriptions and also a limited acess to healthcare support tools.
**Medaura** was created to address this challenge by introducing a **hybrid offline-online medication management system**. The application allows users to: 
- Record and manage their **prescriptions**.
- Receive **timely reminders with alarms** for each medication.
- **Confirm doses** after intake to prevent double-dosing.
- Store all activity **locally** on the device, ensuring functionality even when offline.
- **Synchronize** medication data to the cloud once connectivity is restored.
- The application's architecture merges the **reliability of local offline databases** with the **scalability and interconnectivity of cloud systems**, enabling seamless synchronization and remote healthcare monitoring. Through this approach, Medaura not only assists patients in managing their medication routines but also empowers **doctors, caregivers, and family members** to monitor adherence remotely in real time.
## Problem Statement
Chronic diseases such as **diabetes, kidney failure, hypertension, and asthma** have become a major public health challenge across Africa. According to the World Health Organization (WHO), non-communicable diseases now account for a growing percentage of hospital visits and deaths on the continent. Effective management of these conditions requires patients to adhere strictly to prescribed medication schedules - missing even a few doses can lead to complications, hospitalization, or, in severe cases, death.
Unfortunately, medication adherence remains a major issue due to several compounding factors:
1.**Forgetfulness and poor routine tracking:**
Many patients;especially the elderly and sometimes chronically ill individuals find it difficult to remember when and how to take their medications. The lack of simple reminder tools makes consistent adherence nearly impossible.
2.**Limited access to healthcare technology:**
Modern reminder apps exist, but most require a **constant internet connectivity** and **smartphone literacy**. These requirements exclude millions of people in rural or low-income communities where network coverage is poor and digital literacy is limited.
3.**Inadequate monitoring by caregivers and doctors:**
In many cases, healthcare providers lose visibility once a patient leaves the clinic. Without remote monitoring or feedback systems, it becomes challenging to track whether patients are following their treatment plans accurately.
4.**Complexity of existing solutions:**
Many of the currently available medication reminder applications are either too complicated for elder patients or are designed primarily for urban populations with steady internet access. Their interfaces, registration steps, and dependency on cloud-based authentication make them less suitable for low-connectivity environments.
5.**Unreliable connectivty across Africa:**
Internet outages and high data costs further limits the usability of cloud-only healthcare systems. As a result, patients in rural regions often cannot benefit from these digital health innovations.
These above problems collectively contribute to **poor medication adherence**, **increased disease progression**, and **avoidable hospitalizations**; worsening public health outcomes and placing additional strain on already limited healthcare resources.
### Why this problem matters.
Medication non-adherence is not merely an individual issue, it is a **health system inefficiency**. Studies show that in developing regions, **over 50% of patients fail to take their medications as prescribed**, leading to further health complications and costs.
This makes it essential to design a **context-aware**, **offline-capable**, and **user-friendly** solution that bridges the gap between technology and accessibility; a system tailored for Africa's connectivity and healthcare realities.
That is where **Medaura** comes in: a distributed, offline-first medication reminder system that ensures **no patient is left behind** due to internet or infrastructure limitations.
4. Project Objectives

Medaura was created with the goal of addressing real-world medication adherence challenges affecting millions of patients across Africa. The project aims to combine simplicity, accessibility, reliability, and modern distributed systems principles to ensure that patients can manage their treatments effectively, even in areas with unstable or nonexistent internet connectivity. The main objectives include:

4.1 Improve Medication Adherence

Medication non-adherence is responsible for worsening health conditions, unnecessary hospital admissions, and increased mortality. Medaura’s core objective is to help patients remember their medication schedules through a combination of:

Local reminders,

Alarm notifications,

Daily medication progress tracking,

And confirmation prompts to reduce double-dosing.

By reducing missed or incorrect doses, Medaura directly contributes to better treatment outcomes.

4.2 Provide Offline Medication Tracking

Many existing health apps require constant internet access, making them unsuitable for rural or low-connectivity areas. Medaura ensures that:

All medication schedules,

Logs,

Doses,

And notifications
continue to work 100% offline using an embedded SQLite database.

This ensures reliability and makes the app accessible to older patients or patients in remote villages.

4.3 Enable Cloud Synchronization for Remote Monitoring

When internet becomes available, Medaura securely syncs local data with a cloud backend. This objective supports:

Remote follow-up by doctors,

Data sharing with caregivers,

Retrieval of records even when a device is lost,

And multi-device access to the same patient account.

This enables a distributed healthcare ecosystem.

4.4 Build a Scalable Distributed System

From a technical perspective, Medaura demonstrates how distributed systems can be applied to healthcare by achieving:

Fault tolerance (local node continues operating offline)

Eventual consistency (data syncs when network returns)

Scalability (cloud backend supports thousands of users)

Replication (cloud stores consistent, up-to-date copies)

Lightweight communication between devices and cloud

4.5 Ensure Accessibility and Ease of Use

Medaura is designed with a friendly interface that older users and patients with limited digital literacy can understand. This includes:

Large fonts,

Simple buttons,

Minimalistic layout,

Clear icons,

And intuitive scheduling flows.

The goal is inclusiveness — healthcare should never be complicated.
 5. System Architecture

Medaura uses a hybrid distributed architecture combining offline-first mobile functionality with cloud-based synchronization. The entire system consists of three major components:

Client Node (Mobile App)

Local Database (SQLite)

Cloud Backend (FastAPI Server + Cloud Database)

Below is a detailed look at each layer.

5.1 Client Node (Mobile App)

Each user’s device acts as an independent node in the distributed system. This node is responsible for:

Storing user data locally

Scheduling medication alarms

Managing time-based triggers

Allowing dose confirmations

Handling offline functionality

Syncing records to cloud only when internet exists

Because each mobile app functions independently, Medaura achieves fault tolerance — even if the cloud is unreachable, no functionality is lost on the patient side.

5.2 Local Storage (SQLite Database)

SQLite is chosen for its:

Lightweight nature,

High reliability,

Zero configuration,

Excellent performance on mobile devices.

This database stores:

Medication name

Dosage

Start and end dates

Frequency (morning, afternoon, evening, or specific times)

Alarms and reminders

Doses taken/not taken

Sync status (“pending” or “synced”)

The local database acts as the first layer of the distributed system — a private storage node that ensures data persistence even without internet.

5.3 Cloud Backend (FastAPI Server)

The cloud backend is responsible for:

Storing global patient records

Synchronizing data from multiple devices

Providing an API for users and caregivers

Managing authentication

Ensuring data replication and backups

Offering scalability for large user bases

The backend runs using:

FastAPI for fast, asynchronous API endpoints

PostgreSQL or MongoDB for persistent cloud storage

JWT for security

Uvicorn/Gunicorn for deployment

Load balancing support (NGINX / cloud provider LB)

This enables Medaura to function as a distributed healthcare platform, not just a standalone app.

6. How Medaura Works (Step-by-Step Flow)

This section explains the internal logic of Medaura.

6.1 Medication Creation Flow

User enters medication details.

Data is saved locally in SQLite.

App registers one or multiple alarms depending on schedule.

A “pending_sync” flag is attached if the device is offline.

The medication now exists independently from the cloud.

6.2 Alarm and Notification Flow

The alarm system works entirely offline through:

Android AlarmManager

Flutter Local Notifications Plugin

iOS UNUserNotificationCenter

Workflow:

At the scheduled time, the app wakes up.

Alarm sound + notification is displayed.

User confirms or dismisses the dose.

Confirmation is stored locally.

No internet needed.

6.3 Synchronization Flow (Cloud Interaction)

When internet becomes available:

App checks SQLite for any “pending_sync” entries.

App sends the data to the cloud backend using HTTPS APIs.

Cloud stores updated records.

Server responds with consistency confirmation.

Local database updates the sync status to “synced.”

If caregiver or doctor modified something, updates are downloaded.

This creates eventual consistency between local nodes and the cloud.
 7. Distributed Systems Concepts in Medaura

This section links Medaura directly to distributed systems principles.

7.1 Fault Tolerance

Medaura continues working even when:

Internet is unavailable

Cloud server is down

User is in a remote area

Because all operations are handled locally, the system is naturally fault-tolerant.

7.2 Scalability

Cloud backend supports:

Horizontal scaling

Multiple server instances

Load balancing

Data partitioning

Caching

This ensures performance even with thousands of users.

7.3 Replication

Cloud database replicates patient data across:

Multiple availability zones

Backup nodes

Failover servers

This improves reliability and availability.

7.4 Eventual Consistency

Local app + cloud sync = eventually consistent distributed system.

The system does not require instant consistency — as long as updates eventually reach the cloud, the system stays correct.

7.5 Distributed Nodes

Each device acts as an independent node and communicates with the central FastAPI node.
Together, these form a distributed network of:

Patient devices

Cloud servers

Caregiver/doctor dashboards
 8. Features of Medaura

List the main features clearly and professionally.

Offline medication scheduling

Local alarms and reminders

Dose confirmation system

Cloud synchronization

Multi-device access

Doctor/caregiver portal

Medication history logs

Simple and accessible UI

Secure authentication

Backup and restore via cloud
 9. Tech Stack

Frontend / Mobile App:

Flutter

Dart

Local Notifications Plugin

SQLite

Backend:

FastAPI

Python

PostgreSQL or MongoDB

JWT Authentication

Cloud hosting (Railway, AWS, Render, or DigitalOcean)
 10. Future Improvements

Adding AI-based reminder predictions

SMS notifications for feature phones

Multi-language support

Wearable-device integration

Emergency alerts for missed doses

Dashboard for hospitals

Real-time syncing
