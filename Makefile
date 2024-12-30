
.PHONY: uninstall_all_dependencies

run:
	python3 src/main.py

install:
	pip install -e . -U

install_dev:
	pip install -e .[dev,test] -U

uninstall_all_dependencies:
	pip freeze | grep -v '^-e' | xargs pip uninstall -y
	pip cache purge

#test:
#	pytest tests/

gen_proto:
	python -m grpc_tools.protoc -I . --python_betterproto_out=src/proto_gen proto/example.proto

gen_ca_cert:
	openssl genrsa -out cert/ca.key 4096
	openssl req -x509 -new -nodes -key cert/ca.key -sha256 -days 365 -out cert/ca.crt \
	-subj "/C=RU/ST=State/L=City/O=Organization/OU=OrgUnit/CN=Test"

gen_server_cert:
	openssl genrsa -out cert/server.key 4096
	openssl req -new -key cert/server.key -out cert/server.csr \
	-subj "/C=RU/ST=State/L=City/O=Organization/OU=ServerUnit/CN=localhost"
	openssl x509 -req -in cert/server.csr -CA cert/ca.crt -CAkey cert/ca.key -CAcreateserial -out cert/server.crt -days 365 -sha256

gen_client_cert:
	openssl genrsa -out cert/client.key 4096
	openssl req -new -key cert/client.key -out cert/client.csr \
	-subj "/C=RU/ST=State/L=City/O=Organization/OU=ClientUnit/CN=client"
	openssl x509 -req -in cert/client.csr -CA cert/ca.crt -CAkey cert/ca.key -CAcreateserial -out cert/client.crt -days 365 -sha256

lint:
	ruff check .
	ruff format . --check

format:
	ruff check . --fix
	ruff format .

clean:
	rm -rf src/*.egg-info *.egg_info __pycache__ build/
	@echo "🧹🧹🧹 perfect"
