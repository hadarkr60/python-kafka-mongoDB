# Flask Message Queuing with Kafka

This project lets you buy products and manage a sample shop inventory using message queuing and a MongoDB database.

---

## Introduction

The project has two web pages:
- **Client Page**: Allows clients to buy products.
- **Admin Page**: Allows shop management to handle inventory.

The backend uses the web pages to interact with users, generating API messages that are sent to Kafka topics. An API server listens as a Kafka consumer, processing messages to update the MongoDB database accordingly.

---

## Project Flow

![Project Flow](./seqence_diagram_image.png)  

---

## Prerequisites
- **Python** and required project modules installed
- **MongoDB**: Configured with a shop database and two collections for inventory and purchase history
- **Kafka**: Configured Kafka broker and topics


