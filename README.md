  ## Installation

  ```bash
  git clone $repo

  # run typesense in docker (or use typesense cloud)
  # link: https://typesense.org/docs/guide/install-typesense.html#option-2-local-machine-self-hosting
  export TYPESENSE_API_KEY=xyz

  mkdir "$(pwd)"/typesense-data

  docker run -d -p 8108:8108 \
              -v"$(pwd)"/typesense-data:/data typesense/typesense:26.0 \
              --data-dir /data \
              --api-key=$TYPESENSE_API_KEY \
              --enable-cors

  ```
