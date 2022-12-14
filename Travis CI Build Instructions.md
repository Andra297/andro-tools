### 11. Create An Account in Travis CI for Building the Recovery
- Go to https://travis-ci.com/ and SignUp there using GitHub. Then add the repository there.
- After adding the repo, from repository `Settings`, you need to add a few secrets as environment variables.
  - Add "GitOAUTHToken" as New Environment Variables' _Name_ and put your GitHub Token's value as it's _Value_ here.
  - Go to [Docker Hub](https://hub.docker.com/) and SignUp there. Put the username as "DOCKER_USERNAME" and password/token as "DOCKER_PASSWORD".

### 12. Create A File Named `.travis.yml` in GitHub Repo
- To Start the Build Process, go to your created TWRP Device Tree in GitHub.
- Make a file named `.travis.yml` with below content
  ```yaml
  os: linux
  dist: focal
  group: edge
  language: generic
  git:
    depth: 1
  addons:
    apt:
      update:
        - true
      packages:
        - aria2
        - zstd
        - xz-utils
  services:
    - docker
  before_install:
    - echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin 2>/dev/null
    - docker pull fr3akyphantom/droid-builder:latest
  before_script:
    - cd $HOME && mkdir twrp
    # Download the TWRP Compressed Source Files from PhantomZone54's Release
    # > More on https://github.com/PhantomZone54/twrp_sources_norepo/releases/latest
    # Uncomment & Use below line If Building for Lollipop-based Devices
    # - TWRP_SOURCE="https://github.com/PhantomZone54/twrp_sources_norepo/releases/download/v3.4.0-20201103/MinimalOmniRecovery-twrp-5.1-norepo-20201103.tzst"
    # Use below line If Building for Marshmallow-based Devices
    - TWRP_SOURCE="https://github.com/PhantomZone54/twrp_sources_norepo/releases/download/v3.4.0-20201103/MinimalOmniRecovery-twrp-6.0-norepo-20201103.tzst"
    # Uncomment & Use below line If Building for Nougat-based Devices
    # - TWRP_SOURCE="https://github.com/PhantomZone54/twrp_sources_norepo/releases/download/v3.4.0-20201103/MinimalOmniRecovery-twrp-7.1-norepo-20201103.tzst"
    - aria2c -x16 -s8 --console-log-level=error --summary-interval=0 "${TWRP_SOURCE}" -o twrp.tzst || wget -q --show-progress --progress=bar:force "${TWRP_SOURCE}" -O twrp.tzst
    - tar --zstd -xf twrp.tzst --directory $HOME/twrp/ && rm twrp.tzst
    # If Building for Oreo-based Devices
    # - TWRP_SOURCE1="https://github.com/PhantomZone54/twrp_sources_norepo/releases/download/v3.4.0-20201103/MinimalOmniRecovery-twrp-8.1-norepo-20201103.tzst.aa" && TWRP_SOURCE2="https://github.com/PhantomZone54/twrp_sources_norepo/releases/download/v3.4.0-20201103/MinimalOmniRecovery-twrp-8.1-norepo-20201103.tzst.ab"
    # If Building for Oreo-based Devices
    # - TWRP_SOURCE1="https://github.com/PhantomZone54/twrp_sources_norepo/releases/download/v3.4.0-20201103/MinimalOmniRecovery-twrp-9.0-norepo-20201103.tzst.aa" && TWRP_SOURCE2="https://github.com/PhantomZone54/twrp_sources_norepo/releases/download/v3.4.0-20201103/MinimalOmniRecovery-twrp-9.0-norepo-20201103.tzst.ab" && TWRP_SOURCE3="https://github.com/PhantomZone54/twrp_sources_norepo/releases/download/v3.4.0-20201103/MinimalOmniRecovery-twrp-9.0-norepo-20201103.tzst.ac" && TWRP_SOURCE4="https://github.com/PhantomZone54/twrp_sources_norepo/releases/download/v3.4.0-20201103/MinimalOmniRecovery-twrp-9.0-norepo-20201103.tzst.ad"
    # Then uncomment below lines to download & extract the multi-part files
    # - aria2c -x16 -s8 --console-log-level=error --summary-interval=0 "${TWRP_SOURCE1}" "${TWRP_SOURCE2}" "${TWRP_SOURCE3}" "${TWRP_SOURCE4}" || wget -q --show-progress --progress=bar:force "${TWRP_SOURCE1}" "${TWRP_SOURCE2}" "${TWRP_SOURCE3}" "${TWRP_SOURCE4}"
    # - tar --zstd -xf MinimalOmniRecovery-twrp-*.*-norepo-2020*.tzst.aa --directory $HOME/twrp/ && rm MinimalOmniRecovery*.tzst.*
  script:
    # Replace your ${_USERNAME_}, ${_REPO_SLUG_}, ${_VENDORNAME_}, ${_CODENAME_}
    - cd $HOME/twrp/ && git clone https://github.com/${_USERNAME_}/${_REPO_SLUG_}.git device/${_VENDORNAME_}/${_CODENAME_}
    - rm -rf bootable/recovery && git clone https://github.com/omnirom/android_bootable_recovery -b android-9.0 --depth 1 bootable/recovery
    - |
      docker run --rm -i -e USER_ID=$(id -u) -e GROUP_ID=$(id -g) -v "$(pwd):/home/builder/twrp/:rw,z" -v "${HOME}/.ccache:/srv/ccache:rw,z" fr3akyphantom/droid-builder bash << EOF
      cd /home/builder/twrp/
      source build/envsetup.sh
      # Choose build flavor as "eng" or "userdebug"
      BUILD_FLAVOR="eng"
      lunch omni_${_CODENAME_}-${BUILD_FLAVOR}
      make -j$(nproc --all) recoveryimage
      exit
      EOF
  after_success:
    - export version=$(cat bootable/recovery/variables.h | grep "define TW_MAIN_VERSION_STR" | cut -d '"' -f2)
    - cp $HOME/twrp/out/target/product/${_CODENAME_}/recovery.img $HOME/twrp/TWRP-$version-${_CODENAME_}-$(date +"%Y%m%d")-Unofficial.img
    - cd $HOME/twrp/
    # Optional: You might need to switch from https://transfer.sh to https://file.io
    # - curl -s --upload-file TWRP-$version-${_CODENAME_}-$(date +"%Y%m%d")-Unofficial.img https://transfer.sh/ && echo ""
  deploy:
    provider: releases
    # The secret api_key will be loaded from the environment variables
    token: $GitOAUTHToken
    cleanup: false
    file_glob: true
    file: $HOME/twrp/*.img
    on:
      tags: false # Set "true" to deploy only on successful tagged commit builds
      repo: ${_USERNAME_}/${_REPO_SLUG_} # Optional: If you want to deploy on different repository
      branch: master # Optional: Needs to be exact as the config branch
  branches:
    only:
      - master # Set travis builder branch(es) names
    except:
      - /^(?i:untagged)-.*$/
      - /^v\d+\.\d+(\.\d+)?(-\S*)?$/
  ```

### 13. Fire-Up The Build
- When you save the .travis.yml file for the first time, the build will automatically start.
  - You can see the progress of the build on https://travis-ci.com/${_USERNAME_}/${_REPO_SLUG_}/
- After the first build, you can see the result on the GitHub Repository's Releases Page at https://github.com/${_USERNAME_}/${_REPO_SLUG_}/releases/

### 14. Flash and Enjoy
- Flash the newly-build Recovery. It is better Not to Use with Stock ROM.

### 15. Troubleshooting Recovery Boot
- If The Recovery does not Boot,
  - [x] Unpack the Stock Recovery Image again, and double-check properties used in TWRP Tree
  - [x] Double-check files that are included in the Tree
- If the Recovery starts Upside-Down,
  - [x] Edit BoardConfig.mk and insert the below line before the `include` part (last line)
    ```makefile
    BOARD_HAS_FLIPPED_SCREEN := true
    ```
