SHELL := /bin/bash

.PHONY: platform-up platform-down platform-ps platform-logs platform-doctor

platform-up:
	./run-local.sh

platform-down:
	docker compose stop sentiment-platform-api sentiment-platform-web local-portal

platform-ps:
	docker compose ps sentiment-platform-api sentiment-platform-web local-portal

platform-logs:
	docker compose logs -f sentiment-platform-api sentiment-platform-web local-portal

platform-doctor:
	./tools/platform-doctor.sh
