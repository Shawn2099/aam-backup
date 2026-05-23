

## Introduction
Restic is a fast and secure backup program. In the following sections, we will present
typical workflows, starting with installing, preparing a new repository, and making the
first backup.
## Quickstart Guide
To get started with a local repository, first define some environment variables:
export RESTIC_REPOSITORY=/srv/restic-repo
export RESTIC_PASSWORD=some-strong-password

Initialize the repository (first time only):
restic init

Create your first backup:
restic backup ~/work

You can list all the snapshots you created with:
restic snapshots

You can restore a backup by noting the snapshot ID you want and running:
restic restore --target /tmp/restore-work your-snapshot-ID

It is a good idea to periodically check your repository’s metadata:
restic check

or full data:
restic check --read-data


## Packages
Note that if at any point the package you’re trying to use is outdated, you always have
the option to use an official binary from the restic project.
These are up to date binaries, built in a reproducible and verifiable way, that you can
download and run without having to do additional installation work.
Please see the Official Binaries section below for various downloads. Official binaries
can be updated in place by using the restic self-update command.
## Alpine Linux
On Alpine Linux you can install the restic package from the official community repos,
e.g. using apk:
apk add restic

## Arch Linux
On Arch Linux, there is a package called restic installed from the official community
repos, e.g. with pacman -S:
pacman -S restic

## Debian
On Debian, there’s a package called restic which can be installed from the official
repos, e.g. with
apt-get:

apt-get install restic

## Fedora
restic can be installed using dnf:
dnf install restic

If you used restic from copr previously, remove the copr repo as follows to avoid any
conflicts:
dnf copr remove copart/restic

## Gentoo Linux
On Gentoo Linux, you can install the restic package from the official repos using emerge:
emerge restic

macOS
If you are using macOS, you can install restic using Homebrew:
brew install restic

On Linux and macOS, you can also install it using pkgx:
pkgx install restic

You may also install it using MacPorts:
sudo port install restic


Nix & NixOS
If you are using Nix / NixOS there is a package available named restic. It can be
installed using nix-env:
nix-env --install restic

OpenBSD
On OpenBSD 6.3 and greater, you can install restic using pkg_add:
pkg_add restic

FreeBSD
On FreeBSD (11 and probably later versions), you can install restic using pkg install:
pkg install restic

openSUSE
On openSUSE (leap 15.0 and greater, and tumbleweed), you can install restic using the
zypper package manager:
zypper install restic

RHEL & CentOS
For RHEL / CentOS Stream 8 & 9 restic can be installed from the EPEL repository:
dnf install epel-release
dnf install restic


For RHEL7/CentOS there is a copr repository available, you can try the following:
yum install yum-plugin-copr
yum copr enable copart/restic
yum install restic

If that doesn’t work, you can try adding the repository directly, for CentOS6 use:
yum-config-manager --add-repo
https://copr.fedorainfracloud.org/coprs/copart/restic/repo/epel-6/copart-restic-epel-6
## .repo

For CentOS7 use:
yum-config-manager --add-repo
https://copr.fedorainfracloud.org/coprs/copart/restic/repo/epel-7/copart-restic-epel-7
## .repo

## Solus
restic can be installed from the official repo of Solus via the eopkg package manager:
eopkg install restic

## Windows
restic can be installed using either Scoop or WinGet.
Regardless of the method, the restic.exe binary will be added to your PATH
automatically, making the
restic command accessible in Powershell or CMD.
scoop install restic


winget install --exact --id restic.restic --scope Machine

By default, WinGet will install restic into the User scope, which is typically in your user’s
%LOCALAPPDATA% directory. This behavior may be undesirable for system-wide backups, so
specifying
--scope Machine is recommended so that restic is installed into %ProgramFiles%.
This requires elevation.
## Official Binaries
## Stable Releases
You can download the latest stable release versions of restic from the restic release
page. These builds are considered stable and releases are made regularly in a
controlled manner.
There’s both pre-compiled binaries for different platforms as well as the source code
available for download. Just download and run the one matching your system.
On your first installation, if you desire, you can verify the integrity of your downloads by
testing the SHA-256 checksums listed in
SHA256SUMS and verifying the integrity of the file
SHA256SUMS with the PGP signature in SHA256SUMS.asc. The PGP signature was created
using the key (0x91A6868BD3F7A907):
pub   4096R/91A6868BD3F7A907 2014-11-01
Key fingerprint = CF8F 18F2 8445 7597 3F79  D4E1 91A6 868B D3F7 A907
uid                          Alexander Neumann <alexander@bumpern.de>
sub   4096R/D5FC2ACF4043FDF1 2014-11-01

Once downloaded, the official binaries can be updated in place using the restic
self-update
command (needs restic 0.9.3 or later):
restic version
restic 0.9.3 compiled with go1.11.2 on linux/amd64

restic self-update

find latest release of restic at GitHub
latest version is 0.9.4
download file SHA256SUMS
download SHA256SUMS
download file SHA256SUMS
download SHA256SUMS.asc
GPG signature verification succeeded
download restic_0.9.4_linux_amd64.bz2
downloaded restic_0.9.4_linux_amd64.bz2
saved 12115904 bytes in ./restic
successfully updated restic to version 0.9.4

restic version
restic 0.9.4 compiled with go1.12.1 on linux/amd64

The self-update command uses the GPG signature on the files uploaded to GitHub to
verify their authenticity. No external programs are necessary.
## Note
Please be aware that the user executing the restic self-update command must have
the permission to replace the restic binary. If you want to save the downloaded restic
binary into a different file, pass the file name via the option
## --output.
## Unstable Builds
Another option is to use the latest builds for the master branch, available on the restic
beta download site. These too are pre-compiled and ready to run, and a new version is
built every time a push is made to the master branch.
## Docker Container
We’re maintaining a bare docker container with just a few files and the restic binary, you
can get it with docker pull like this:
docker pull restic/restic


The container is also available on the GitHub Container Registry:
docker pull ghcr.io/restic/restic

Restic relies on the hostname for various operations. Make sure to set a static
hostname using –hostname when creating a Docker container, otherwise Docker will
assign a random hostname each time.
## From Source
restic is written in the Go programming language and you need at least Go version 1.23.
Building restic may also work with older versions of Go, but that’s not supported. See
the Getting started guide of the Go project for instructions how to install Go.
In order to build restic from source, execute the following steps:
git clone https://github.com/restic/restic
## [...]

cd restic

go run build.go

You can easily cross-compile restic for all supported platforms, just supply the target OS
and platform via the command-line options like this (for Windows and FreeBSD
respectively):
go run build.go --goos windows --goarch amd64

go run build.go --goos freebsd --goarch 386

go run build.go --goos linux --goarch arm --goarm 6

go run build.go --goos solaris --goarch amd64

The resulting binary is statically linked and does not require any libraries.

At the moment, the only tested compiler for restic is the official Go compiler. Building
restic with gccgo may work, but is not supported.
## Autocompletion
Restic can write out man pages and bash/fish/zsh/powershell compatible
autocompletion scripts:
./restic generate --help

The "generate" command writes automatically generated files (like the man pages
and the auto-completion files for bash, fish, zsh and powershell).

## Usage:
restic generate [flags] [command]

## Flags:
--bash-completion file   write bash completion file
--fish-completion file   write fish completion file
-h, --help                   help for generate
--man directory          write man pages to directory
--powershell-completion  write powershell completion file
--zsh-completion file    write zsh completion file

Example for using sudo to write a bash completion script directly to the system-wide
location:
sudo ./restic generate --bash-completion /etc/bash_completion.d/restic
writing bash completion file to /etc/bash_completion.d/restic

Example for using sudo to write a zsh completion script directly to the system-wide
location:
sudo ./restic generate --zsh-completion /usr/local/share/zsh/site-functions/_restic
writing zsh completion file to /usr/local/share/zsh/site-functions/_restic

## Note

The path for the --bash-completion option may vary depending on the operating system
used, e.g.
/usr/share/bash-completion/completions/restic in Debian and derivatives.
Please look up the correct path in the appropriate documentation.
Example for setting up a powershell completion script for the local user’s profile:
# Create profile if one does not exist
If (!(Test-Path $PROFILE.CurrentUserAllHosts)) {New-Item -Path
$PROFILE.CurrentUserAllHosts -Force}

$ProfileDir = (Get-Item $PROFILE.CurrentUserAllHosts).Directory

# Generate Restic completions in the same directory as the profile
restic generate --powershell-completion "$ProfileDir\restic-completion.ps1"

# Append to the profile file the command to load Restic completions
Add-Content -Path $PROFILE.CurrentUserAllHosts -Value "`r`nImport-Module
$ProfileDir\restic-completio


Preparing a new repository
The place where your backups will be saved is called a “repository”. This is simply a
directory containing a set of subdirectories and files created by restic to store your
backups, some corresponding metadata and encryption keys.
To access the repository, a password (also called a key) must be specified. A repository
can hold multiple keys that can all be used to access the repository.
This chapter explains how to create (“init”) such a repository. The repository can be
stored locally, or on some remote server or service. We’ll first cover using a local
repository; the remaining sections of this chapter cover all the other options. You can
skip to the next chapter once you’ve read the relevant section here.
For automated backups, restic supports specifying the repository location in the
environment variable
RESTIC_REPOSITORY. Restic can also read the repository location

from a file specified via the --repository-file option or the environment variable
## RESTIC_REPOSITORY_FILE.
For automating the supply of the repository password to restic, several options exist:
● Setting the environment variable RESTIC_PASSWORD
● Specifying the path to a file with the password via the option --password-file
or the environment variable
## RESTIC_PASSWORD_FILE
● Configuring a program to be called when the password is needed via the
option
--password-command or the environment variable RESTIC_PASSWORD_COMMAND
The init command has an option called --repository-version which can be used to
explicitly set the version of the new repository. By default, the current stable version is
used (see table below). The alias
latest will always resolve to the latest repository
version. Have a look at the design documentation for more details.
The below table shows which restic version is required to use a certain repository
version, as well as notable features introduced in the various versions.
## Repository
version
Required restic
version
Major new
features
## Comment
## 1
## Any

## 2
0.14.0 or newer
## Compression
support
## Current
default

## Local
In order to create a repository at /srv/restic-repo, run the following command and enter
the same password twice:
restic init --repo /srv/restic-repo
enter password for new repository:
enter password again:
created restic repository 085b3c76b9 at /srv/restic-repo
Please note that knowledge of your password is required to access the repository.
Losing your password means that your data is irrecoverably lost.

## Warning
Remembering your password is important! If you lose it, you won’t be able to access
data stored in the repository.
## Warning
On Linux, storing the backup repository on a CIFS (SMB) share or backing up data from
a CIFS share is not recommended due to compatibility issues in older Linux kernels.
Either use another backend or set the environment variable GODEBUG to
asyncpreemptoff=1. Refer to GitHub issue #2659 for further explanations.
## SFTP
In order to backup data via SFTP, you must first set up a server with SSH and let it know
your public key. Passwordless login is important since automatic backups are not
possible if the server prompts for credentials.
Once the server is configured, the setup of the SFTP repository can simply be achieved
by changing the URL scheme in the
init command:

restic -r sftp:user@host:/srv/restic-repo init
enter password for new repository:
enter password again:
created restic repository f1c6108821 at sftp:user@host:/srv/restic-repo
Please note that knowledge of your password is required to access the repository.
Losing your password means that your data is irrecoverably lost.

You can also specify a relative (read: no slash (/) character at the beginning) directory,
in this case the dir is relative to the remote user’s home directory.
Also, if the SFTP server is enforcing domain-confined users, you can specify the user
this way:
user@domain@host.
## Note
Please be aware that SFTP servers do not expand the tilde character (~) normally used
as an alias for a user’s home directory. If you want to specify a path relative to the
user’s home directory, pass a relative path to the SFTP backend.
If you need to specify a port number or IPv6 address, you’ll need to use URL syntax.
E.g., the repository
/srv/restic-repo on [::1] (localhost) at port 2222 with username
user can be specified as
sftp://user@[::1]:2222//srv/restic-repo

Note the double slash: the first slash separates the connection settings from the path,
while the second is the start of the path. To specify a relative path, use one slash.
Alternatively, you can create an entry in the ssh configuration file, usually located in your
home directory at
~/.ssh/config or in /etc/ssh/ssh_config:
Host foo
User bar
## Port 2222


Then use the specified host name foo normally (you don’t need to specify the user
name in this case):
$ restic -r sftp:foo:/srv/restic-repo init

You can also add an entry with a special host name which does not exist, just for use
with restic, and use the
Hostname option to set the real host name:
Host restic-backup-host
Hostname foo
User bar
## Port 2222

Then use it in the backend specification:
$ restic -r sftp:restic-backup-host:/srv/restic-repo init

Last, if you’d like to use an entirely different program to create the SFTP connection,
you can specify the command to be run with the option
-o sftp.command="foobar".
## Alternatively,
-o sftp.args allows setting the arguments passed to the default SSH
command (ignored when
sftp.command is set)
## Note
Please be aware that SFTP servers close connections when no data is received by the
client. This can happen when restic is processing huge amounts of unchanged data. To
avoid this issue add the following lines to the client’s .ssh/config file:
ServerAliveInterval 60
ServerAliveCountMax 240

REST Server

In order to backup data to the remote server via HTTP or HTTPS protocol, you must
first set up a remote REST server instance. Once the server is configured, accessing it
is achieved by changing the URL scheme like this:
restic -r rest:http://host:8000/ init

Depending on your REST server setup, you can use HTTPS protocol, unix socket,
password protection, multiple repositories or any combination of those features. The
TCP/IP port is also configurable. Here are some more examples:
restic -r rest:https://host:8000/ init
restic -r rest:https://user:pass@host:8000/ init
restic -r rest:https://user:pass@host:8000/my_backup_repo/ init
restic -r rest:http+unix:///tmp/rest.socket:/my_backup_repo/ init

The server username and password can be specified using environment variables as
well:
export RESTIC_REST_USERNAME=<MY_REST_SERVER_USERNAME>
export RESTIC_REST_PASSWORD=<MY_REST_SERVER_PASSWORD>

If you use TLS, restic will use the system’s CA certificates to verify the server certificate.
When the verification fails, restic refuses to proceed and exits with an error. If you have
your own self-signed certificate, or a custom CA certificate should be used for
verification, you can pass restic the certificate filename via the
--cacert option. It will
then verify that the server’s certificate is contained in the file passed to this option, or
signed by a CA certificate in the file. In this case, the system CA certificates are not
considered at all.
REST server uses exactly the same directory structure as local backend, so you should
be able to access it both locally and via HTTP, even simultaneously.
## Amazon S3

Restic can backup data to any Amazon S3 bucket. However, in this case, changing the
URL scheme is not enough since Amazon uses special security credentials to sign
HTTP requests. By consequence, you must first setup the following environment
variables with the credentials you obtained while creating the bucket.
export AWS_ACCESS_KEY_ID=<MY_ACCESS_KEY>
export AWS_SECRET_ACCESS_KEY=<MY_SECRET_ACCESS_KEY>

When using temporary credentials make sure to include the session token via the
environment variable
## AWS_SESSION_TOKEN.
You can then easily initialize a repository that uses your Amazon S3 as a backend.
Make sure to use the endpoint for the correct region. The example uses
us-east-1. If the
bucket does not exist it will be created in that region:
restic -r s3:s3.us-east-1.amazonaws.com/bucket_name init
enter password for new repository:
enter password again:
created restic repository eefee03bbd at s3:s3.us-east-1.amazonaws.com/bucket_name
Please note that knowledge of your password is required to access the repository.
Losing your password means that your data is irrecoverably lost.

Until version 0.8.0, restic used a default prefix of restic, so the files in the bucket were
placed in a directory named
restic. If you want to access a repository created with an
older version of restic, specify the path after the bucket name like this:
restic -r s3:s3.us-east-1.amazonaws.com/bucket_name/restic [...]

## Note
restic expects path-style URLs like for example s3.us-west-2.amazonaws.com/bucket_name
for Amazon S3. Virtual-hosted–style URLs like bucket_name.s3.us-west-2.amazonaws.com,
where the bucket name is part of the hostname are not supported. These must be

converted to path-style URLs instead, for example
s3.us-west-2.amazonaws.com/bucket_name. See below for configuration options for
S3-compatible storage from other providers.
## Minio Server
Minio is an Open Source Object Storage, written in Go and compatible with Amazon S3
## API.
● Download and Install Minio Download.
● You can also refer to Minio Docs for step by step guidance on installation and
getting started on Minio Client and Minio Server.
You must first setup the following environment variables with the credentials of your
## Minio Server.
export AWS_ACCESS_KEY_ID=<YOUR-MINIO-ACCESS-KEY-ID>
export AWS_SECRET_ACCESS_KEY=<YOUR-MINIO-SECRET-ACCESS-KEY>

Now you can easily initialize restic to use Minio server as a backend with this command.
restic -r s3:http://localhost:9000/restic init
enter password for new repository:
enter password again:
created restic repository 6ad29560f5 at s3:http://localhost:9000/restic
Please note that knowledge of your password is required to access
the repository. Losing your password means that your data is irrecoverably lost.

## S3-compatible Storage
For an S3-compatible storage service that is not Amazon, you can specify the URL to
the server like this:
s3:https://server:port/bucket_name.
You must also set credentials for authentication to the service.

export AWS_ACCESS_KEY_ID=<YOUR-ACCESS-KEY-ID>
export AWS_SECRET_ACCESS_KEY=<YOUR-SECRET-ACCESS-KEY>
restic -r s3:https://server:port/bucket_name init

If needed, you can manually specify the region to use by either setting the environment
variable
AWS_DEFAULT_REGION or calling restic with an option parameter like -o
s3.region="us-east-1"
. If the region is not specified, the default region us-east-1 is used.
To select between path-style and virtual-hosted access, the extended option -o
s3.bucket-lookup=auto
can be used. It supports the following values:
● auto: Default behavior. Uses dns for Amazon and Google endpoints. Uses path
for all other endpoints
● dns: Use virtual-hosted-style bucket access
● path: Use path-style bucket access
Certain S3-compatible servers do not properly implement the ListObjectsV2 API, most
notably Ceph versions before v14.2.5. On these backends, as a temporary workaround,
you can provide the
-o s3.list-objects-v1=true option to use the older ListObjects API
instead. This option may be removed in future versions of restic.
## Wasabi
S3 storage from Wasabi can be used as follows.
● Determine the correct Wasabi service URL for your bucket here.
● Set environment variables with the necessary account credentials
export AWS_ACCESS_KEY_ID=<YOUR-WASABI-ACCESS-KEY-ID>
export AWS_SECRET_ACCESS_KEY=<YOUR-WASABI-SECRET-ACCESS-KEY>
restic -r s3:https://<WASABI-SERVICE-URL>/<WASABI-BUCKET-NAME> init


Alibaba Cloud (Aliyun) Object Storage System
## (OSS)
S3 storage from Alibaba OSS can be used as follows.
● Determine the correct Alibaba OSS region endpoint - this will be something
like oss-eu-west-1.aliyuncs.com
● You will need the region name too - this will be something like oss-eu-west-1
● Set environment variables with the necessary account credentials
export AWS_ACCESS_KEY_ID=<YOUR-OSS-ACCESS-KEY-ID>
export AWS_SECRET_ACCESS_KEY=<YOUR-OSS-SECRET-ACCESS-KEY>
restic -o s3.bucket-lookup=dns -o s3.region=<OSS-REGION> -r
s3:https://<OSS-ENDPOINT>/<OSS-BUCKET-NAME> init

OpenStack Swift
Restic can backup data to an OpenStack Swift container. Because Swift supports
various authentication methods, credentials are passed through environment variables.
In order to help integration with existing OpenStack installations, the naming convention
of those variables follows the official Python Swift client:
For keystone v1 authentication
export ST_AUTH=<MY_AUTH_URL>
export ST_USER=<MY_USER_NAME>
export ST_KEY=<MY_USER_PASSWORD>

For keystone v2 authentication (some variables are optional)
export OS_AUTH_URL=<MY_AUTH_URL>
export OS_REGION_NAME=<MY_REGION_NAME>
export OS_USERNAME=<MY_USERNAME>
export OS_PASSWORD=<MY_PASSWORD>
export OS_TENANT_ID=<MY_TENANT_ID>
export OS_TENANT_NAME=<MY_TENANT_NAME>

For keystone v3 authentication (some variables are optional)
export OS_AUTH_URL=<MY_AUTH_URL>
export OS_REGION_NAME=<MY_REGION_NAME>
export OS_USERNAME=<MY_USERNAME>
export OS_USER_ID=<MY_USER_ID>
export OS_PASSWORD=<MY_PASSWORD>

export OS_USER_DOMAIN_NAME=<MY_DOMAIN_NAME>
export OS_USER_DOMAIN_ID=<MY_DOMAIN_ID>
export OS_PROJECT_NAME=<MY_PROJECT_NAME>
export OS_PROJECT_DOMAIN_NAME=<MY_PROJECT_DOMAIN_NAME>
export OS_PROJECT_DOMAIN_ID=<MY_PROJECT_DOMAIN_ID>
export OS_TRUST_ID=<MY_TRUST_ID>

For keystone v3 application credential authentication (application credential id)
export OS_AUTH_URL=<MY_AUTH_URL>
export OS_APPLICATION_CREDENTIAL_ID=<MY_APPLICATION_CREDENTIAL_ID>
export OS_APPLICATION_CREDENTIAL_SECRET=<MY_APPLICATION_CREDENTIAL_SECRET>

For keystone v3 application credential authentication (application credential name)
export OS_AUTH_URL=<MY_AUTH_URL>
export OS_USERNAME=<MY_USERNAME>
export OS_USER_DOMAIN_NAME=<MY_DOMAIN_NAME>
export OS_APPLICATION_CREDENTIAL_NAME=<MY_APPLICATION_CREDENTIAL_NAME>
export OS_APPLICATION_CREDENTIAL_SECRET=<MY_APPLICATION_CREDENTIAL_SECRET>

For authentication based on tokens
export OS_STORAGE_URL=<MY_STORAGE_URL>
export OS_AUTH_TOKEN=<MY_AUTH_TOKEN>

Restic should be compatible with an OpenStack RC file in most cases.
Once environment variables are set up, a new repository can be created. The name of
the Swift container and optional path can be specified. If the container does not exist, it
will be created automatically:
restic -r swift:container_name:/path init   # path is optional
enter password for new repository:
enter password again:
created restic repository eefee03bbd at swift:container_name:/path
Please note that knowledge of your password is required to access the repository.
Losing your password means that your data is irrecoverably lost.

The policy of the new container created by restic can be changed using environment
variable:
export SWIFT_DEFAULT_CONTAINER_POLICY=<MY_CONTAINER_POLICY>

## Backblaze B2

## Warning
Due to issues with error handling in the current B2 library that restic uses, the
recommended way to utilize Backblaze B2 is by using its S3-compatible API.
Follow the documentation to generate S3-compatible access keys and then setup restic
as described at Amazon S3. This is expected to work better than using the Backblaze
B2 backend directly.
Different from the B2 backend, restic’s S3 backend will only hide no longer necessary
files. By default, Backblaze B2 retains all of the different versions of the files and “hides”
the older versions. Thus, to free space occupied by hidden files, it is recommended to
use the B2 lifecycle “Keep only the last version of the file”. The previous version of the
file is “hidden” for one day and then deleted automatically by B2. More details at the
Backblaze documentation.
Restic can backup data to any Backblaze B2 bucket. You need to first setup the
following environment variables with the credentials you can find in the dashboard on
the “Buckets” page when signed into your B2 account:
export B2_ACCOUNT_ID=<MY_APPLICATION_KEY_ID>
export B2_ACCOUNT_KEY=<MY_APPLICATION_KEY>

To get application keys, a user can go to the App Keys section of the Backblaze account
portal. You must create a master application key first. From there, you can generate a
standard Application Key. Please note that the Application Key should be treated like a
password and will only appear once. If an Application Key is forgotten, you must
generate a new one.
For more information on application keys, refer to the Backblaze documentation.

## Note
As of version 0.9.2, restic supports both master and non-master application keys. If
using a non-master application key, ensure that it is created with at least read and write
access to the B2 bucket. On earlier versions of restic, a master application key is
required.
You can then initialize a repository stored at Backblaze B2. If the bucket does not exist
yet and the credentials you passed to restic have the privilege to create buckets, it will
be created automatically:
restic -r b2:bucketname:path/to/repo init
enter password for new repository:
enter password again:
created restic repository eefee03bbd at b2:bucketname:path/to/repo
Please note that knowledge of your password is required to access the repository.
Losing your password means that your data is irrecoverably lost.

Note that the bucket name must be unique across all of B2.
The number of concurrent connections to the B2 service can be set with the -o
b2.connections=10
switch. By default, at most five parallel connections are established.
## Microsoft Azure Blob Storage
You can also store backups on Microsoft Azure Blob Storage. Export the Azure Blob
Storage account name:
export AZURE_ACCOUNT_NAME=<ACCOUNT_NAME>

For authentication export one of the following variables:
For storage account key
export AZURE_ACCOUNT_KEY=<SECRET_KEY>

For SAS
export AZURE_ACCOUNT_SAS=<SAS_TOKEN>

For authentication using az login ensure the user has the minimum permissions of the
role assignment
Storage Blob Data Contributor on Azure RBAC for the storage account.
az login

Alternatively, if run on Azure, restic will automatically use service accounts configured
via the standard environment variables or Workload / Managed Identities.
To enforce the use of the Azure CLI credential when other credentials are present, set
the following environment variable:
export AZURE_FORCE_CLI_CREDENTIAL=true

Restic will by default use Azure’s global domain core.windows.net as endpoint suffix. You
can specify other suffixes as follows:
export AZURE_ENDPOINT_SUFFIX=<ENDPOINT_SUFFIX>

Afterwards you can initialize a repository in a container called foo in the root path like
this:
restic -r azure:foo:/ init
enter password for new repository:
enter password again:

created restic repository a934bac191 at azure:foo:/
## [...]


The number of concurrent connections to the Azure Blob Storage service can be set
with the
-o azure.connections=10 switch. By default, at most five parallel connections are
established.
The access tier of the blobs uploaded to the Azure Blob Storage service can be set with
the
-o azure.access-tier=Cool switch. The allowed values are Hot, Cool or Cold. If
unspecified, the default is inferred from the default configured on the storage account.
## Google Cloud Storage
## Note
Google Cloud Storage is not the same service as Google Drive - to use the latter,
please see Other Services via rclone for instructions on using the rclone backend.
Restic supports Google Cloud Storage as a backend and connects via a service
account.
For normal restic operation, the service account must have the
storage.objects.{create,delete,get,list} permissions for the bucket. These are
included in the “Storage Object Admin” role.
restic init can create the repository
bucket. Doing so requires the
storage.buckets.create permission (“Storage Admin” role).
If the bucket already exists, that permission is unnecessary.
To use the Google Cloud Storage backend, first create a service account key and
download the JSON credentials file. Second, find the Google Project ID that you can
see in the Google Cloud Platform console at the “Storage/Settings” menu. Export the
path to the JSON key file and the project ID as follows:
export GOOGLE_PROJECT_ID=123123123123
export GOOGLE_APPLICATION_CREDENTIALS=$HOME/.config/gs-secret-restic-key.json


Restic uses Google’s client library to generate default authentication material, which
means if you’re running in Google Container Engine or are otherwise located on an
instance with default service accounts then these should work out of the box.
Alternatively, you can specify an existing access token directly:
export GOOGLE_ACCESS_TOKEN=ya29.a0AfH6SMC78...

If GOOGLE_ACCESS_TOKEN is set all other authentication mechanisms are disabled. The
access token must have at least the
https://www.googleapis.com/auth/devstorage.read_write scope. Keep in mind that access
tokens are short-lived (usually one hour), so they are not suitable if creating a backup
takes longer than that, for instance.
Once authenticated, you can use the gs: backend type to create a new repository in the
bucket
foo at the root path:
restic -r gs:foo:/ init
enter password for new repository:
enter password again:

created restic repository bde47d6254 at gs:foo/
## [...]

The number of concurrent connections to the GCS service can be set with the -o
gs.connections=10
switch. By default, at most five parallel connections are established.
The region, where a bucket should be created, can be specified with the -o gs.region=us
switch. By default, the region is set to
us.
Other Services via rclone
The program rclone can be used to access many other different services and store data
there. First, you need to install and configure rclone. The general backend specification

format is rclone:<remote>:<path>, the <remote>:<path> component will be directly passed
to rclone. When you configure a remote named
foo, you can then call restic as follows to
initiate a new repository in the path
bar in the remote foo:
restic -r rclone:foo:bar init

Restic takes care of starting and stopping rclone.
## Note
If you get an error message saying “cannot implicitly run relative executable rclone
found in current directory”, this means that an rclone executable was found in the
current directory. For security reasons restic will not run this implicitly, instead you have
to use the
-o rclone.program=./rclone extended option to override this security check
and explicitly tell restic to use the executable.
As a more concrete example, suppose you have configured a remote named b2prod for
Backblaze B2 with rclone, with a bucket called
yggdrasil. You can then use rclone to list
files in the bucket like this:
rclone ls b2prod:yggdrasil

In order to create a new repository in the root directory of the bucket, call restic like this:
restic -r rclone:b2prod:yggdrasil init

If you want to use the path foo/bar/baz in the bucket instead, pass this to restic:
restic -r rclone:b2prod:yggdrasil/foo/bar/baz init


Listing the files of an empty repository directly with rclone should return a listing similar
to the following:
rclone ls b2prod:yggdrasil/foo/bar/baz
155 bar/baz/config
448 bar/baz/keys/4bf9c78049de689d73a56ed0546f83b8416795295cda12ec7fb9465af3900b44

Rclone can be configured with environment variables, so for instance configuring a
bandwidth limit for rclone can be achieved by setting the RCLONE_BWLIMIT environment
variable:
export RCLONE_BWLIMIT=1M

For debugging rclone, you can set the environment variable RCLONE_VERBOSE=2.
The rclone backend has three additional options:
● -o rclone.program specifies the path to rclone, the default value is just rclone
● -o rclone.args allows setting the arguments passed to rclone, by default this
is
serve restic --stdio --b2-hard-delete
● -o rclone.timeout specifies timeout for waiting on repository opening, the
default value is
## 1m
The reason for the --b2-hard-delete parameters can be found in the corresponding
GitHub issue #1657.
In order to start rclone, restic will build a list of arguments by joining the following lists (in
this order):
rclone.program, rclone.args and as the last parameter the value that follows
the
rclone: prefix of the repository specification.
So, calling restic like this
restic -o rclone.program="/path/to/rclone" \

-o rclone.args="serve restic --stdio --bwlimit 1M --b2-hard-delete --verbose" \
-r rclone:b2:foo/bar

runs rclone as follows:
/path/to/rclone serve restic --stdio --bwlimit 1M --b2-hard-delete --verbose
b2:foo/bar

Manually setting rclone.program also allows running a remote instance of rclone e.g. via
SSH on a server, for example:
restic -o rclone.program="ssh user@remotehost rclone" -r rclone:b2:foo/bar

With these options, restic works with local files. It uses rclone and credentials stored on
remotehost to communicate with B2. All data (except credentials) is encrypted/decrypted
locally, then sent/received via
remotehost to/from B2.
A more advanced version of this setup forbids specific hosts from removing files in a
repository. See the blog post by Simon Ruderich for details and the documentation for
the forget command to learn about important security considerations.
The rclone command may also be hard-coded in the SSH configuration or the user’s
public key, in this case it may be sufficient to just start the SSH connection (and it’s
irrelevant what’s passed after
rclone: in the repository specification):
restic -o rclone.program="ssh user@host" -r rclone:x

Password prompt on Windows
At the moment, restic only supports the default Windows console interaction. If you use
emulation environments like MSYS2 or Cygwin, which use terminals like Mintty or rxvt,
you may get a password error.

You can workaround this by using a special tool called winpty (look here and here for
detail information). On MSYS2, you can install winpty as follows:
pacman -S winpty
winpty restic -r /srv/restic-repo init

Group accessible repositories
Since restic version 0.14 local and SFTP repositories can be made accessible to
members of a system group. To control this we have to change the group permissions
of the top-level
config file and restic will use this as a hint to determine what permissions
to apply to newly created files. By default
restic init sets repositories up to be group
inaccessible.
In order to give group members read-only access we simply add the read permission bit
to all repository files with
chmod:
chmod -R g+r /srv/restic-repo

This serves two purposes: 1) it sets the read permission bit on the repository config file
triggering restic’s logic to create new files as group accessible and 2) it actually allows
the group read access to the files.
## Note
By default files on Unix systems are created with a user’s primary group as defined by
the gid (group id) field in /etc/passwd. See passwd(5).
For read-write access things are a bit more complicated. When users other than the
repository creator add new files in the repository they will be group-owned by this user’s
primary group by default, not that of the original repository owner, meaning the original
creator wouldn’t have access to these files. That’s hardly what you’d want.

To make this work we can employ the help of the setgid permission bit available on
Linux and most other Unix systems. This permission bit makes newly created
directories inherit both the group owner (gid) and setgid bit from the parent directory.
Setting this bit requires root but since it propagates down to any new directories we only
have to do this privileged setup once:
find /srv/restic-repo -type d -exec chmod g+s '{}' \;
chmod -R g+rw /srv/restic-repo

This sets the setgid bit on all existing directories in the repository and then grants
read/write permissions for group access.
## Note
To manage who has access to the repository you can use usermod on Linux systems, to
change which group controls repository access
chgrp -R is your friend.
Repositories with empty password
Restic by default refuses to create or operate on repositories that use an empty
password. Since restic 0.17.0, the option
--insecure-no-password allows disabling this
check. Restic will not prompt for a password when using this option. Specifying
--insecure-no-password while also passing a password to restic via a CLI option or via
environment variable results in an error.
For security reasons, the option must always be specified when operating on
repositories with an empty password. For example to create a new repository with an
empty password, use the following command.
restic init --insecure-no-password


The init and copy commands also support the option --from-insecure-no-password which
applies to the source repository. The
key add and key passwd commands include the
--new-insecure-no-password option to add or set an empty password.
Backing up
Now we’re ready to backup some data. The contents of a directory at a specific point in
time is called a “snapshot” in restic. Run the following command and enter the
repository password you chose above again:
restic -r /srv/restic-repo --verbose backup ~/work
open repository
enter password for repository:
repository a14e5863 opened (version 2, compression level auto)
load index files
start scan on [/home/user/work]
start backup on [/home/user/work]
scan finished in 1.837s: 5307 files, 1.720 GiB

Files:        5307 new,     0 changed,     0 unmodified
Dirs:         1867 new,     0 changed,     0 unmodified
Added to the repository: 1.200 GiB (1.103 GiB stored)

processed 5307 files, 1.720 GiB in 0:12
snapshot 40dc1520 saved

As you can see, restic created a backup of the directory and was pretty fast! The
specific snapshot just created is identified by a sequence of hexadecimal characters,
40dc1520 in this case.
You can see that restic tells us it processed 1.720 GiB of data, this is the size of the files
and directories in
~/work on the local file system. It also tells us that only 1.200 GiB was
added to the repository. This means that some of the data was duplicate and restic was
able to efficiently reduce it. The data compression also managed to compress the data
down to 1.103 GiB.

If you don’t pass the --verbose option, restic will print less data. You’ll still get a nice live
status display. Be aware that the live status shows the processed files and not the
transferred data. Transferred volume might be lower (due to de-duplication) or higher.
On Windows, the --use-fs-snapshot option will use Windows’ Volume Shadow Copy
Service (VSS) when creating backups. Restic will transparently create a VSS snapshot
for each volume that contains files to backup. Files are read from the VSS snapshot
instead of the regular filesystem. This allows to backup files that are exclusively locked
by another process during the backup.
You can use the following extended options to change the VSS behavior:
● -o vss.timeout specifies timeout for VSS snapshot creation, default value
being 120 seconds
● -o vss.exclude-all-mount-points disable auto snapshotting of all volume
mount points
● -o vss.exclude-volumes allows excluding specific volumes or volume mount
points from snapshotting
● -o vss.provider specifies VSS provider used for snapshotting
For example a 2.5 minutes timeout with snapshotting of mount points disabled can be
specified as:
-o vss.timeout=2m30s -o vss.exclude-all-mount-points=true

and excluding drive d:\, mount point c:\mnt and volume
\\?\Volume{04ce0545-3391-11e0-ba2f-806e6f6e6963}\ as:
-o vss.exclude-volumes="d:;c:\mnt\;\\?\volume{04ce0545-3391-11e0-ba2f-806e6f6e6963}"


VSS provider can be specified by GUID:
-o vss.provider={3f900f90-00e9-440e-873a-96ca5eb079e5}

or by name:
-o vss.provider="Hyper-V IC Software Shadow Copy Provider"

Also, MS can be used as alias for Microsoft Software Shadow Copy provider 1.0.
By default VSS ignores Outlook OST files. This is not a restriction of restic but the
default Windows VSS configuration. The files not to snapshot are configured in the
Windows registry under the following key:
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\BackupRestore\FilesNotToSnapshot

For more details refer the official Windows documentation e.g. the article Registry Keys
and Values for Backup and Restore
## .
If you run the backup command again, restic will create another snapshot of your data,
but this time it’s even faster and no new data was added to the repository (since all data
is already there). This is de-duplication at work!
restic -r /srv/restic-repo --verbose backup ~/work
open repository
enter password for repository:
repository a14e5863 opened (version 2, compression level auto)
load index files
using parent snapshot 40dc1520
start scan on [/home/user/work]
start backup on [/home/user/work]
scan finished in 1.881s: 5307 files, 1.720 GiB

Files:           0 new,     0 changed,  5307 unmodified
Dirs:            0 new,     0 changed,  1867 unmodified
Added to the repository: 0 B   (0 B   stored)


processed 5307 files, 1.720 GiB in 0:03
snapshot 79766175 saved

You can even backup individual files in the same repository (not passing --verbose
means less output):
restic -r /srv/restic-repo backup ~/work.txt
enter password for repository:
snapshot 249d0210 saved

If you’re interested in what restic does, pass --verbose twice (or --verbose=2) to display
detailed information about each file and directory restic encounters:
echo 'more data foo bar' >> ~/work.txt

restic -r /srv/restic-repo --verbose --verbose backup ~/work.txt
open repository
enter password for repository:
lock repository
load index files
using parent snapshot f3f8d56b
start scan
start backup
scan finished in 2.115s
modified  /home/user/work.txt, saved in 0.007s (22 B added)
modified  /home/user/, saved in 0.008s (0 B added, 378 B metadata)
modified  /home/, saved in 0.009s (0 B added, 375 B metadata)
processed 22 B in 0:02
Files:           0 new,     1 changed,     0 unmodified
Dirs:            0 new,     2 changed,     0 unmodified
Data Blobs:      1 new
Tree Blobs:      3 new
Added:      1.116 KiB
snapshot 8dc503fc saved

In fact several hosts may use the same repository to backup directories and files
leading to a greater de-duplication.

Now is a good time to run restic check to verify that all data is properly stored in the
repository. You should run this command regularly to make sure the internal structure of
the repository is free of errors.
File change detection
When restic encounters a file that has already been backed up, whether in the current
backup or a previous one, it makes sure the file’s content is only stored once in the
repository. To do so, it normally has to scan the entire content of the file. Because this
can be very expensive, restic also uses a change detection rule based on file metadata
to determine whether a file is likely unchanged since a previous backup. If it is, the file is
not scanned again.
The previous backup snapshot, called “parent” snapshot in restic terminology, is
determined as follows. By default restic groups snapshots by hostname and backup
paths, and then selects the latest snapshot in the group that matches the current
backup. You can change the selection criteria using the
--group-by option, which
defaults to
host,paths. To select the latest snapshot with the same paths independent of
the hostname, use
paths. Or, to only consider the hostname and tags, use host,tags.
Alternatively, it is possible to manually specify a specific parent snapshot using the
--parent option. Finally, note that one would normally set the --group-by option for the
forget command to the same value.
Change detection is only performed for regular files (not special files, symlinks or
directories) that have the exact same path as they did in a previous backup of the same
location. If a file or one of its containing directories was renamed, it is considered a
different file and its entire contents will be scanned again.
Metadata changes (permissions, ownership, etc.) are always included in the backup,
even if file contents are considered unchanged.

On Unix (including Linux and Mac), given that a file lives at the same location as a file
in a previous backup, the following file metadata attributes have to match for its
contents to be presumed unchanged:
● Modification timestamp (mtime).
● Metadata change timestamp (ctime).
● File size.
● Inode number (internal number used to reference a file in a filesystem).
The reason for requiring both mtime and ctime to match is that Unix programs can freely
change mtime (and some do). In such cases, a ctime change may be the only hint that
a file did change.
The following restic backup command line flags modify the change detection rules:
● --force: turn off change detection and rescan all files.
● --ignore-ctime: require mtime to match, but allow ctime to differ.
● --ignore-inode: require mtime to match, but allow inode number
and ctime to differ.
The option --ignore-inode exists to support FUSE-based filesystems and pCloud, which
do not assign stable inodes to files.
Note that the device id of the containing mount point is never taken into account. Device
numbers are not stable for removable devices and ZFS snapshots. If you want to force
a re-scan in such a case, you can change the mountpoint.
On Windows, a file is considered unchanged when its path, size and modification time
match, and only
--force has any effect. The other options are recognized but ignored.
Skip creating snapshots if unchanged

By default, restic always creates a new snapshot even if nothing has changed
compared to the parent snapshot. To omit the creation of a new snapshot in this case,
specify the
--skip-if-unchanged option.
Note that when using absolute paths to specify the backup source, then also changes to
the parent folders result in a changed snapshot. For example, a backup of
/home/user/work will create a new snapshot if the metadata of either /, /home or
/home/user change. To avoid this problem run restic from the corresponding folder and
use relative paths.
cd /home/user/work && restic -r /srv/restic-repo backup . --skip-if-unchanged

open repository
enter password for repository:
repository a14e5863 opened (version 2, compression level auto)
load index files
using parent snapshot 40dc1520
start scan on [.]
start backup on [.]
scan finished in 1.814s: 5307 files, 1.720 GiB

Files:           0 new,     0 changed,  5307 unmodified
Dirs:            0 new,     0 changed,  1867 unmodified
Added to the repository: 0 B   (0 B   stored)

processed 5307 files, 1.720 GiB in 0:03
skipped creating snapshot

## Dry Runs
You can perform a backup in dry run mode to see what would happen without modifying
the repository.
● --dry-run/-n Report what would be done, without writing to the repository
Combined with --verbose, you can see a list of changes:
restic -r /srv/restic-repo backup ~/work --dry-run -vv | grep "added"
modified  /plan.txt, saved in 0.000s (9.110 KiB added)
modified  /archive.tar.gz, saved in 0.140s (25.542 MiB added)

Would be added to the repository: 25.551 MiB

## Excluding Files
You can exclude folders and files by specifying exclude patterns, currently the exclude
options are:
● --exclude Specified one or more times to exclude one or more items
● --iexclude Same as --exclude but ignores the case of paths
● --exclude-caches Specified once to exclude a folder’s content if it contains the
special CACHEDIR.TAG file, but keep CACHEDIR.TAG.
● --exclude-file Specified one or more times to exclude items listed in a given
file
● --iexclude-file Same as exclude-file but ignores cases like in --iexclude
● --exclude-if-present foo Specified one or more times to exclude a folder’s
content if it contains a file called
foo (optionally having a given header, no
wildcards for the file name supported)
● --exclude-larger-than size Specified once to exclude files larger than the
given size
● --exclude-cloud-files Specified once to exclude online-only cloud files (such
as OneDrive Files On-Demand), currently only supported on Windows
Please see restic help backup for more specific information about each exclude option.
Let’s say we have a file called excludes.txt with the following content:
# exclude go-files
## *.go
# exclude foo/x/y/z/bar foo/x/bar foo/bar
foo/**/bar

It can be used like this:

restic -r /srv/restic-repo backup ~/work --exclude="*.c" --exclude-file=excludes.txt

This instructs restic to exclude files matching the following criteria:
● All files matching *.c (parameter --exclude)
● All files matching *.go (second line in excludes.txt)
● All files and sub-directories named bar which reside somewhere below a
directory called
foo (fourth line in excludes.txt)
Patterns use the syntax of the Go function filepath.Match and are tested against the full
path of a file/dir to be saved, even if restic is passed a relative path to save. Empty lines
and lines starting with a
# are ignored.
Environment variables in exclude files are expanded with os.ExpandEnv, so
/home/$USER/foo will be expanded to /home/bob/foo for the user bob. To get a literal dollar
sign, write
$$ to the file - this has to be done even when there’s no matching
environment variable for the word following a single
$. Note that tilde (~) is not
expanded, instead use the
$HOME or equivalent environment variable (depending on your
operating system).
Patterns need to match on complete path components. For example, the pattern foo:
● matches /dir1/foo/dir2/file and /dir/foo
● does not match /dir/foobar or barfoo
A trailing / is ignored, a leading / anchors the pattern at the root directory. This means,
/bin matches /bin/bash but does not match /usr/bin/restic.
Regular wildcards cannot be used to match over the directory separator /, e.g. b*ash
matches
/bin/bash but does not match /bin/ash. To match across an arbitrary number of
subdirectories, use the special
** wildcard. The ** must be positioned between path
separators. The pattern
foo/**/bar matches:

## ● /dir1/foo/dir2/bar/file
## ● /foo/bar/file
## ● /tmp/foo/bar
Spaces in patterns listed in an exclude file can be specified verbatim. That is, in order to
exclude a file named
foo bar star.txt, put that just as it reads on one line in the exclude
file. Please note that beginning and trailing spaces are trimmed - in order to match
these, use e.g. a
- at the beginning or end of the filename.
Spaces in patterns listed in the other exclude options (e.g. --exclude on the command
line) are specified in different ways depending on the operating system and/or shell.
Restic itself does not need any escaping, but your shell may need some escaping in
order to pass the name/pattern as a single argument to restic.
On most Unixy shells, you can either quote or use backslashes. For example:
● --exclude='foo bar star/foo.txt'
● --exclude="foo bar star/foo.txt"
● --exclude=foo\ bar\ star/foo.txt
If a pattern starts with exclamation mark and matches a file that was previously matched
by a regular pattern, the match is cancelled. It works similarly to
gitignore, with the
same limitation: once a directory is excluded, it is not possible to include files inside the
directory. Here is a complete example to backup a selection of directories inside the
home directory. It works by excluding any directory, then selectively add back some of
them.
## $HOME/*
!$HOME/Documents
!$HOME/code
!$HOME/.emacs.d
!$HOME/games
## # [...]
node_modules
## *~

## *.o
## *.lo
## *.pyc

By specifying the option --one-file-system you can instruct restic to only backup files
from the file systems the initially specified files or directories reside on. In other words, it
will prevent restic from crossing filesystem boundaries and subvolumes when
performing a backup.
For example, if you backup / with this option and you have external media mounted
under
/media/usb then restic will not back up /media/usb at all because this is a different
filesystem than
/. Virtual filesystems such as /proc are also considered different and
thereby excluded when using
## --one-file-system:
restic -r /srv/restic-repo backup --one-file-system /

Please note that this does not prevent you from specifying multiple filesystems on the
command line, e.g:
restic -r /srv/restic-repo backup --one-file-system / /media/usb

will back up both the / and /media/usb filesystems, but will not include other filesystems
like
/sys and /proc.
## Note
--one-file-system is currently unsupported on Windows, and will cause the backup to
immediately fail with an error.
Files larger than a given size can be excluded using the –exclude-larger-than option:
restic -r /srv/restic-repo backup ~/work --exclude-larger-than 1M


This excludes files in ~/work which are larger than 1 MiB from the backup.
The default unit for the size value is bytes, so e.g. --exclude-larger-than 2048 would
exclude files larger than 2048 bytes (2 KiB). To specify other units, suffix the size value
with one of
k/K for KiB (1024 bytes), m/M for MiB (1024^2 bytes), g/G for GiB (1024^3
bytes) and
t/T for TiB (1024^4 bytes), e.g. 1k, 10K, 20m, 20M, 30g, 30G, 2t or 2T).
## Including Files
The options --files-from, --files-from-verbatim and --files-from-raw allow you to give
restic a file containing lists of file patterns or paths to be backed up. This is useful e.g.
when you want to back up files from many different locations, or when you use some
other software to generate the list of files to back up.
The argument passed to --files-from must be the name of a text file that contains one
pattern per line. The file must be encoded as UTF-8, or UTF-16 with a byte-order mark.
Leading and trailing whitespace is removed from the patterns. Empty lines and lines
starting with a
# are ignored and each pattern is expanded when read, such that special
characters in it are expanded according to the syntax described in the documentation of
the Go function filepath.Match.
The argument passed to --files-from-verbatim must be the name of a text file that
contains one path per line, e.g. as generated by GNU
find with the -print flag. Unlike
--files-from, --files-from-verbatim does not expand any special characters in the list of
paths, does not strip off any whitespace and does not ignore lines starting with a
## #. This
option simply reads and uses each line as-is, although empty lines are still ignored. Use
this option when you want to backup a list of filenames containing the special characters
that would otherwise be expanded when using
## --files-from.

The --files-from-raw option is a variant of --files-from-verbatim that requires each line
in the file to be terminated by an ASCII NUL character (the
\0 zero byte) instead of a
newline, so that it can even handle file paths containing newlines in their name or are
not encoded as UTF-8 (except on Windows, where the listed filenames must still be
encoded in UTF-8. This option is the safest choice when generating the list of filenames
from a script (e.g. GNU
find with the -print0 flag).
All three options interpret the argument - as standard input and will read the list of
files/patterns from there instead of a text file.
In all cases, paths may be absolute or relative to restic backup’s working directory.
For example, maybe you want to backup files which have a name that matches a
certain regular expression pattern (uses GNU
find):
find /tmp/some_folder -regex PATTERN -print0 > /tmp/files_to_backup

You can then use restic to backup the filtered files:
restic -r /srv/restic-repo backup --files-from-raw /tmp/files_to_backup

You can combine all three options with each other and with the normal file arguments:
restic backup --files-from /tmp/files_to_backup /tmp/some_additional_file
restic backup --files-from /tmp/glob-pattern --files-from-raw /tmp/generated-list
## /tmp/some_additional_file

## Comparing Snapshots
Restic has a diff command which shows the difference between two snapshots and
displays a small statistic, just pass the command two snapshot IDs:
restic -r /srv/restic-repo diff 5845b002 2ab627a6

comparing snapshot ea657ce5 to 2ab627a6:

## M    /restic/cmd_diff.go
## +    /restic/foo
## M    /restic/restic

Files:           0 new,     0 removed,     2 changed
Dirs:            1 new,     0 removed
Others:          0 new,     0 removed
Data Blobs:     14 new,    15 removed
Tree Blobs:      2 new,     1 removed
Added:   16.403 MiB
Removed: 16.402 MiB

To only compare files in specific subfolders, you can use the <snapshot>:<subfolder>
syntax, where
snapshot is the ID of a snapshot (or the string latest) and subfolder is a
path within the snapshot. For example, to only compare files in the
/restic folder, you
could use the following command:
restic -r /srv/restic-repo diff 5845b002:/restic 2ab627a6:/restic

By default, the diff command only lists differences in file contents. The flag --metadata
shows changes to file metadata, too.
The characters left of the file path show what has changed for this file:
## +
added
## -
removed
## T
entry type changed

## M
file content
changed
## U
metadata changed
## ?
bitrot detected
Backing up special items and metadata
Symlinks are archived as symlinks, restic does not follow them. When you restore, you
get the same symlink again, with the same link target and the same timestamps.
If there is a bind-mount below a directory that is to be saved, restic descends into it.
Device files are saved and restored as device files. This means that e.g. /dev/sda is
archived as a block device file and restored as such. This also means that the content
of the corresponding disk is not read, at least not from the device file.
By default, restic does not save the access time (atime) for any files or other items,
since it is not possible to reliably disable updating the access time by restic itself. This
means that for each new backup a lot of metadata is written, and the next backup needs
to write new metadata again. If you really want to save the access time for files and
directories, you can pass the
--with-atime option to the backup command.
Backing up full security descriptors on Windows is only possible when the user has
SeBackupPrivilege privilege or is running as admin. This is a restriction of Windows not
restic. If either of these conditions are not met, only the owner, group and DACL will be
backed up.

Note that restic does not back up some metadata associated with files. Of particular
note are:
● File creation date on Unix platforms
● Inode flags on Unix platforms
Reading data from a command
Sometimes, it can be useful to directly save the output of a program, for example,
mysqldump so that the SQL can later be restored. Restic supports this mode of operation;
just supply the option
--stdin-from-command when using the backup action, and write the
command in place of the files/directories. To prevent restic from interpreting the
arguments for the command, make sure to add
-- before the command starts:
restic -r /srv/restic-repo backup --stdin-from-command -- mysqldump --host example
mydb [...]

This command creates a new snapshot based on the standard output of mysqldump. By
default, the command’s standard output is saved in a file named
stdin. A different name
can be specified with
## --stdin-filename:
restic -r /srv/restic-repo backup --stdin-filename production.sql --stdin-from-command
-- mysqldump --host example mydb [...]

Restic uses the command exit code to determine whether the command succeeded. A
non-zero exit code from the command causes restic to cancel the backup. This causes
restic to fail with exit code 1. No snapshot will be created in this case.
Reading data from stdin
## Warning

Restic cannot detect if data read from stdin is complete or not. As explained below, this
can cause incomplete backup unless additional checks (outside of restic) are
configured. If possible, use
--stdin-from-command instead.
Alternatively, restic supports reading arbitrary data directly from the standard input. Use
the option
--stdin of the backup command as follows:
Will not notice failures, see the warning below
gzip bigfile.dat | restic -r /srv/restic-repo backup --stdin

This creates a new snapshot of the content of bigfile.dat. As for --stdin-from-command,
the default file name is
stdin; a different name can be specified with --stdin-filename.
Important: while it is possible to pipe a command output to restic using --stdin, doing
so is discouraged as it will mask errors from the command, leading to corrupted
backups. For example, in the following code block, if
mysqldump fails to connect to the
MySQL database, the restic backup will nevertheless succeed in creating an _empty_
backup:
Will not notice failures, read the warning above
mysqldump [...] | restic -r /srv/restic-repo backup --stdin

A simple solution is to use --stdin-from-command (see above). If you still need to use the
--stdin flag, you must use the shell option set -o pipefail (so that a non-zero exit code
from one of the programs in the pipe makes the whole chain return a non-zero exit
code) and you must check the exit code of the pipe and act accordingly (e.g., remove
the last backup). Refer to the Use the Unofficial Bash Strict Mode for more details on
this.
Tags for backup

Snapshots can have one or more tags, short strings which add identifying information.
Just specify the tags for a snapshot one by one with
## --tag:
restic -r /srv/restic-repo backup --tag projectX --tag foo --tag bar ~/work
## [...]

The tags can later be used to keep (or forget) snapshots with the forget command. The
command
tag can be used to modify tags on an existing snapshot.
Scheduling backups
Restic does not have a built-in way of scheduling backups, as it’s a tool that runs when
executed rather than a daemon. There are plenty of different ways to schedule backup
runs on various different platforms, e.g. systemd and cron on Linux/BSD and Task
Scheduler in Windows, depending on one’s needs and requirements. If you don’t want
to implement your own scheduling, you can use resticprofile.
When scheduling restic to run recurringly, please make sure to detect already running
instances before starting the backup.
Space requirements
Restic currently assumes that your backup repository has sufficient space for the
backup operation you are about to perform. This is a realistic assumption for many
cloud providers, but may not be true when backing up to local disks.
Should you run out of space during the middle of a backup, there will be some
additional data in the repository, but the snapshot will never be created as it would only
be written at the very (successful) end of the backup operation. Previous snapshots will
still be there and will still work.
Exit status codes

Restic returns an exit status code after the backup command is run:
● 0 when the backup was successful (snapshot with all source files created)
● 1 when there was a fatal error (no snapshot created)
● 3 when some source files could not be read (incomplete snapshot with
remaining files created)
● further exit codes are documented in Exit codes.
Fatal errors occur for example when restic is unable to write to the backup destination,
when there are network connectivity issues preventing successful communication, or
when an invalid password or command line argument is provided. When restic returns
this exit status code, one should not expect a snapshot to have been created.
Source file read errors occur when restic fails to read one or more files or directories
that it was asked to back up, e.g. due to permission problems. Restic displays the
number of source file read errors that occurred while running the backup. If there are
errors of this type, restic will still try to complete the backup run with all the other files,
and create a snapshot that then contains all but the unreadable files.
For use of these exit status codes in scripts and other automation tools, see Exit codes.
To manually inspect the exit code in e.g. Linux, run echo $?.
## Environment Variables
In addition to command-line options, restic supports passing various options in
environment variables. The following lists these environment variables:
RESTIC_REPOSITORY_FILE              Name of file containing the repository location
## (replaces --repository-file)

RESTIC_REPOSITORY                   Location of repository (replaces -r)
RESTIC_PASSWORD_FILE                Location of password file (replaces
## --password-file)

RESTIC_PASSWORD                     The actual password for the repository
RESTIC_PASSWORD_COMMAND             Command printing the password for the repository
to stdout


RESTIC_KEY_HINT                     ID of key to try decrypting first, before other
keys

RESTIC_CACERT                       Location(s) of certificate file(s), comma
separated if multiple (replaces --cacert)

RESTIC_TLS_CLIENT_CERT              Location of TLS client certificate and private key
## (replaces --tls-client-cert)

RESTIC_CACHE_DIR                    Location of the cache directory
RESTIC_COMPRESSION                  Compression mode (only available for repository
format version 2)

RESTIC_HOST                         Only consider snapshots for this host / Set the
hostname for the snapshot manually (replaces --host)

RESTIC_PROGRESS_FPS                 Frames per second by which the progress bar is
updated

RESTIC_PACK_SIZE                    Target size for pack files
RESTIC_READ_CONCURRENCY             Concurrency for file reads

TMPDIR                              Location for temporary files (except Windows)
TMP                                 Location for temporary files (only Windows)

AWS_ACCESS_KEY_ID                   Amazon S3 access key ID
AWS_SECRET_ACCESS_KEY               Amazon S3 secret access key
AWS_SESSION_TOKEN                   Amazon S3 temporary session token
AWS_DEFAULT_REGION                  Amazon S3 default region
AWS_PROFILE                         Amazon credentials profile (alternative to
specifying key and region)

AWS_SHARED_CREDENTIALS_FILE         Location of the AWS CLI shared credentials file
## (default: ~/.aws/credentials)

RESTIC_AWS_ASSUME_ROLE_ARN          Amazon IAM Role ARN to assume using discovered
credentials

RESTIC_AWS_ASSUME_ROLE_SESSION_NAME Session Name to use with the role assumption
RESTIC_AWS_ASSUME_ROLE_EXTERNAL_ID  External ID to use with the role assumption
RESTIC_AWS_ASSUME_ROLE_POLICY       Inline Amazion IAM session policy
RESTIC_AWS_ASSUME_ROLE_REGION       Region to use for IAM calls for the role
assumption (default: us-east-1)

RESTIC_AWS_ASSUME_ROLE_STS_ENDPOINT URL to the STS endpoint (default is determined
based on RESTIC_AWS_ASSUME_ROLE_REGION). You generally do not need to set this,
advanced use only.


AZURE_ACCOUNT_NAME                  Account name for Azure
AZURE_ACCOUNT_KEY                   Account key for Azure
AZURE_ACCOUNT_SAS                   Shared access signatures (SAS) for Azure
AZURE_ENDPOINT_SUFFIX               Endpoint suffix for Azure Storage (default:
core.windows.net)

AZURE_FORCE_CLI_CREDENTIAL          Force the use of Azure CLI credentials for
authentication


B2_ACCOUNT_ID                       Account ID or applicationKeyId for Backblaze B2
B2_ACCOUNT_KEY                      Account Key or applicationKey for Backblaze B2

GOOGLE_PROJECT_ID                   Project ID for Google Cloud Storage
GOOGLE_APPLICATION_CREDENTIALS      Application Credentials for Google Cloud Storage
(e.g. $HOME/.config/gs-secret-restic-key.json)


OS_AUTH_URL                         Auth URL for keystone authentication
OS_REGION_NAME                      Region name for keystone authentication

OS_USERNAME                         Username for keystone authentication
OS_USER_ID                          User ID for keystone v3 authentication
OS_PASSWORD                         Password for keystone authentication
OS_TENANT_ID                        Tenant ID for keystone v2 authentication
OS_TENANT_NAME                      Tenant name for keystone v2 authentication

OS_USER_DOMAIN_NAME                 User domain name for keystone authentication
OS_USER_DOMAIN_ID                   User domain ID for keystone v3 authentication
OS_PROJECT_NAME                     Project name for keystone authentication
OS_PROJECT_DOMAIN_NAME              Project domain name for keystone authentication
OS_PROJECT_DOMAIN_ID                Project domain ID for keystone v3 authentication
OS_TRUST_ID                         Trust ID for keystone v3 authentication

OS_APPLICATION_CREDENTIAL_ID        Application Credential ID (keystone v3)
OS_APPLICATION_CREDENTIAL_NAME      Application Credential Name (keystone v3)
OS_APPLICATION_CREDENTIAL_SECRET    Application Credential Secret (keystone v3)

OS_STORAGE_URL                      Storage URL for token authentication
OS_AUTH_TOKEN                       Auth token for token authentication

RCLONE_BWLIMIT                      rclone bandwidth limit

RESTIC_REST_USERNAME                Restic REST Server username
RESTIC_REST_PASSWORD                Restic REST Server password

ST_AUTH                             Auth URL for keystone v1 authentication
ST_USER                             Username for keystone v1 authentication
ST_KEY                              Password for keystone v1 authentication

See Caching for the rules concerning cache locations when RESTIC_CACHE_DIR is not set.
The external programs that restic may execute include rclone (for rclone backends) and
ssh (for the SFTP backend). These may respond to further environment variables and
configuration files; see their respective manuals.
Working with repositories
Listing all snapshots
Now, you can list all the snapshots stored in the repository. The size column only exists
for snapshots created using restic 0.17.0 or later. It reflects the size of the contained
files at the time when the snapshot was created.

restic -r /srv/restic-repo snapshots
enter password for repository:
ID        Date                 Host    Tags   Directory        Size
## -------------------------------------------------------------------------
40dc1520  2015-05-08 21:38:30  kasimir        /home/user/work  20.643GiB
79766175  2015-05-08 21:40:19  kasimir        /home/user/work  20.645GiB
bdbd3439  2015-05-08 21:45:17  luigi          /home/art        3.141GiB
590c8fc8  2015-05-08 21:47:38  kazik          /srv             580.200MiB
9f0bc19e  2015-05-08 21:46:11  luigi          /srv             572.180MiB

You can filter the listing by directory path:
restic -r /srv/restic-repo snapshots --path="/srv"
enter password for repository:
ID        Date                 Host    Tags   Directory  Size
## -------------------------------------------------------------------
590c8fc8  2015-05-08 21:47:38  kazik          /srv       580.200MiB
9f0bc19e  2015-05-08 21:46:11  luigi          /srv       572.180MiB

Or filter by host:
restic -r /srv/restic-repo snapshots --host luigi
enter password for repository:
ID        Date                 Host    Tags   Directory  Size
## -------------------------------------------------------------------
bdbd3439  2015-05-08 21:45:17  luigi          /home/art  3.141GiB
9f0bc19e  2015-05-08 21:46:11  luigi          /srv       572.180MiB

Combining filters is also possible.
Furthermore you can group the output by the same filters (host, paths, tags):
restic -r /srv/restic-repo snapshots --group-by host

enter password for repository:
snapshots for (host [kasimir])
ID        Date                 Host    Tags   Directory        Size
## ------------------------------------------------------------------------
40dc1520  2015-05-08 21:38:30  kasimir        /home/user/work  20.643GiB
79766175  2015-05-08 21:40:19  kasimir        /home/user/work  20.645GiB
2 snapshots
snapshots for (host [luigi])
ID        Date                 Host    Tags   Directory  Size
## -------------------------------------------------------------------

bdbd3439  2015-05-08 21:45:17  luigi          /home/art  3.141GiB
9f0bc19e  2015-05-08 21:46:11  luigi          /srv       572.180MiB
2 snapshots
snapshots for (host [kazik])
ID        Date                 Host    Tags   Directory  Size
## -------------------------------------------------------------------
590c8fc8  2015-05-08 21:47:38  kazik          /srv       580.200MiB
1 snapshots

Listing files in a snapshot
To get a list of the files in a specific snapshot you can use the ls command:
restic ls 073a90db

snapshot 073a90db of [/home/user/work.txt] filtered by [] at 2024-01-21
## 16:51:18.474558607 +0100 CET):

## /home
## /home/user
## /home/user/work.txt

The special snapshot ID latest can be used to list files and directories of the latest
snapshot in the repository. The
--host flag can be used in conjunction to select the latest
snapshot originating from a certain host only.
restic ls --host kasimir latest

snapshot 073a90db of [/home/user/work.txt] filtered by [] at 2024-01-21
## 16:51:18.474558607 +0100 CET):

## /home
## /home/user
## /home/user/work.txt

By default, ls prints all files in a snapshot.
File listings can optionally be filtered by directories. Any positional arguments after the
snapshot ID are interpreted as absolute directory paths, and only files inside those
directories will be listed. Files in subdirectories are not listed when filtering by
directories. If the
--recursive flag is used, then subdirectories are also included. Any

directory paths specified must be absolute (starting with a path separator); paths use
the forward slash ‘/’ as separator.
restic ls latest /home

snapshot 073a90db of [/home/user/work.txt] filtered by [/home] at 2024-01-21
## 16:51:18.474558607 +0100 CET):

## /home
## /home/user

restic ls --recursive latest /home

snapshot 073a90db of [/home/user/work.txt] filtered by [/home] at 2024-01-21
## 16:51:18.474558607 +0100 CET):

## /home
## /home/user
## /home/user/work.txt

To show more details about the files in a snapshot, you can use the --long option. The
columns include file permissions, UID, GID, file size, modification time and file path. For
scripting usage, the
ls command supports the --json flag; the JSON output format is
described at ls.
restic ls --long latest

snapshot 073a90db of [/home/user/work.txt] filtered by [] at 2024-01-21
## 16:51:18.474558607 +0100 CET):

drwxr-xr-x     0     0      0 2024-01-21 16:50:52 /home
drwxr-xr-x     0     0      0 2024-01-21 16:51:03 /home/user
## -rw-r--r--     0     0     18 2024-01-21 16:51:03 /home/user/work.txt

NCDU (NCurses Disk Usage) is a tool to analyse disk usage of directories. The ls
command supports outputting information about a snapshot in the NCDU format using
the
--ncdu option.
You can use it as follows: restic ls latest --ncdu | ncdu -f -

You can use the options --sort and --reverse to tailor ls output to your needs. --sort
can be one of
name | size | time=mtime | atime | ctime | extension. The default sorting
option is
name. The sorting order can be reversed by specifying --reverse.
restic ls --long latest --sort size --reverse

snapshot 711b0bb6 of [/tmp/restic] at 2025-02-03 08:16:05.310764668 +0000 UTC filtered
by []:

## -rw-rw-r--  1000  1000  16772 2025-02-03 08:09:11 /tmp/restic/cmd_find.go
## -rw-rw-r--  1000  1000   3077 2025-02-03 08:15:46 /tmp/restic/conf.py
## -rw-rw-r--  1000  1000   2834 2025-02-03 08:09:35 /tmp/restic/find.go
-rw-rw-r--  1000  1000   1473 2025-02-03 08:15:30 /tmp/restic/010_introduction.rst
drwxrwxr-x  1000  1000      0 2025-02-03 08:15:46 /tmp/restic
dtrwxrwxrwx     0     0      0 2025-02-03 08:14:22 /tmp

restic ls --long latest --sort time

snapshot 711b0bb6 of [/tmp/restic] at 2025-02-03 08:16:05.310764668 +0000 UTC filtered
by []:

## -rw-rw-r--  1000  1000  16772 2025-02-03 08:09:11 /tmp/restic/cmd_find.go
## -rw-rw-r--  1000  1000   2834 2025-02-03 08:09:35 /tmp/restic/find.go
dtrwxrwxrwx     0     0      0 2025-02-03 08:14:22 /tmp
-rw-rw-r--  1000  1000   1473 2025-02-03 08:15:30 /tmp/restic/010_introduction.rst
drwxrwxr-x  1000  1000      0 2025-02-03 08:15:46 /tmp/restic
## -rw-rw-r--  1000  1000   3077 2025-02-03 08:15:46 /tmp/restic/conf.py

Sorting works with option --json as well. Sorting and option --ncdu are mutually
exclusive. It works also without specifying the option
## --long.
restic ls latest --sort extension

snapshot 711b0bb6 of [/tmp/restic] at 2025-02-03 08:16:05.310764668 +0000 UTC filtered
by []:

## /tmp
## /tmp/restic
## /tmp/restic/cmd_find.go
## /tmp/restic/find.go
## /tmp/restic/conf.py
## /tmp/restic/010_introduction.rst

Copying snapshots between repositories

In case you want to transfer snapshots between two repositories, for example from a
local to a remote repository, you can use the
copy command:
restic -r /srv/restic-repo-copy copy --from-repo /srv/restic-repo
repository d6504c63 opened successfully
repository 3dd0878c opened successfully

snapshot 410b18a2 of [/home/user/work] at 2020-06-09 23:15:57.305305 +0200 CEST by
user@kasimir

copy started, this may take a while...
snapshot 7a746a07 saved

snapshot 4e5d5487 of [/home/user/work] at 2020-05-01 22:44:07.012113 +0200 CEST by
user@kasimir

skipping snapshot 4e5d5487, was already copied to snapshot 50eb62b7

The example command copies all snapshots from the source repository
/srv/restic-repo to the destination repository /srv/restic-repo-copy. Snapshots which
have previously been copied between repositories will be skipped by later copy runs.
## Important
This process will have to both download (read) and upload (write) the entire snapshot(s)
due to the different encryption keys used in the source and destination repository. This
may incur higher bandwidth usage and costs than expected during normal backup runs.
## Important
The copying process does not re-chunk files, which may break deduplication between
the files copied and files already stored in the destination repository. This means that
copied files, which existed in both the source and destination repository, may occupy up
to twice their space in the destination repository. See below for how to avoid this.
The source repository is specified with --from-repo or can be read from a file specified
via
--from-repository-file. Both of these options can also be set as environment

variables $RESTIC_FROM_REPOSITORY or $RESTIC_FROM_REPOSITORY_FILE, respectively. For the
source repository the password can be read from a file
--from-password-file or from a
command
--from-password-command. Alternatively the environment variables
$RESTIC_FROM_PASSWORD_COMMAND and $RESTIC_FROM_PASSWORD_FILE can be used. It is also
possible to directly pass the password via
$RESTIC_FROM_PASSWORD. The key which should
be used for decryption can be selected by passing its ID via the flag
--from-key-hint or
the environment variable
## $RESTIC_FROM_KEY_HINT.
## Note
In case the source and destination repository use the same backend, the configuration
options and environment variables used to configure the backend may apply to both
repositories – for example it might not be possible to specify different accounts for the
source and destination repository. You can avoid this limitation by using the rclone
backend along with remotes which are configured in rclone.
## Note
If copy is aborted, copy will resume the interrupted copying when it is run again. It’s
possible that up to 10 minutes of progress can be lost because the repository index is
only updated from time to time.
Filtering snapshots to copy
The list of snapshots to copy can be filtered by host, path in the backup and/or a
comma-separated tag list:
restic -r /srv/restic-repo-copy copy --from-repo /srv/restic-repo --host luigi --path
/srv --tag foo,bar


It is also possible to explicitly specify the list of snapshots to copy, in which case only
these instead of all snapshots will be copied:
restic -r /srv/restic-repo-copy copy --from-repo /srv/restic-repo 410b18a2 4e5d5487
latest

Ensuring deduplication for copied snapshots
Even though the copy command can transfer snapshots between arbitrary repositories,
deduplication between snapshots from the source and destination repository may not
work. To ensure proper deduplication, both repositories have to use the same
parameters for splitting large files into smaller chunks, which requires additional setup
steps. With the same parameters restic will for both repositories split identical files into
identical chunks and therefore deduplication also works for snapshots copied between
these repositories.
The chunker parameters are generated once when creating a new (destination)
repository. That is for a copy destination repository we have to instruct restic to initialize
it using the same chunker parameters as the source repository:
restic -r /srv/restic-repo-copy init --from-repo /srv/restic-repo
## --copy-chunker-params

Note that it is not possible to change the chunker parameters of an existing repository.
Removing files from snapshots
Snapshots sometimes turn out to include more files than intended. Instead of removing
the snapshots entirely and running the corresponding backup commands again (which
is not always practical after the fact) it is possible to remove the unwanted files from
affected snapshots by rewriting them using the
rewrite command:
restic -r /srv/restic-repo rewrite --exclude secret-file

repository c881945a opened (repository version 2) successfully

snapshot 6160ddb2 of [/home/user/work] at 2022-06-12 16:01:28.406630608 +0200 CEST by
user@kasimir

excluding /home/user/work/secret-file
saved new snapshot b6aee1ff

snapshot 4fbaf325 of [/home/user/work] at 2022-05-01 11:22:26.500093107 +0200 CEST by
user@kasimir


modified 1 snapshots

restic -r /srv/restic-repo rewrite --exclude secret-file 6160ddb2
repository c881945a opened (repository version 2) successfully

snapshot 6160ddb2 of [/home/user/work] at 2022-06-12 16:01:28.406630608 +0200 CEST by
user@kasimir

excluding /home/user/work/secret-file
new snapshot saved as b6aee1ff

modified 1 snapshots

The options --exclude, --exclude-file, --iexclude and --iexclude-file are supported.
They behave the same way as for the backup command, see Excluding Files for details.
It is possible to rewrite only a subset of snapshots by filtering them the same way as for
the copy command, see Filtering snapshots to copy.
The option --snapshot-summary can be used to attach summary data to existing
snapshots that do not have this information. When a snapshot summary is created the
only fields added are
TotalFilesProcessed and TotalBytesProcessed.
By default, the rewrite command will keep the original snapshots and create new ones
for every snapshot which was modified during rewriting. The new snapshots are marked
with the tag
rewrite to distinguish them from the original, untouched snapshots.
Alternatively, you can use the --forget option to immediately remove the original
snapshots. In this case, no tag is added to the new snapshots. Please note that this
only removes the snapshots and not the actual data stored in the repository. Run the

prune command afterwards to remove the now unreferenced data (just like when having
used the
forget command).
In order to preview the changes which rewrite would make, you can use the --dry-run
option. This will simulate the rewriting process without actually modifying the repository.
Instead restic will only print the actions it would perform.
## Note
The rewrite command verifies that it does not modify snapshots in unexpected ways
and fails with an
cannot encode tree at "[...]" without loosing information error
otherwise. This can occur when rewriting a snapshot created by a newer version of
restic or some third-party implementation.
To convert a snapshot into the format expected by the rewrite command use restic
repair snapshots <snapshotID>
## .
Modifying metadata of snapshots
Sometimes it may be desirable to change the metadata of an existing snapshot.
Currently, rewriting the hostname and the time of the backup is supported. This is
possible using the
rewrite command with the option --new-host followed by the desired
new hostname or the option
--new-time followed by the desired new timestamp.
restic rewrite --new-host newhost --new-time "1999-01-01 11:11:11"

repository b7dbade3 opened (version 2, compression level auto)
1 / 1 index files loaded

snapshot 8ed674f4 of [/path/to/abc.txt] at 2023-11-27 21:57:52.439139291 +0100 CET by
user@kasimir

setting time to 1999-01-01 11:11:11 +0100 CET
setting host to newhost
saved new snapshot c05da643


modified 1 snapshots

Checking integrity and consistency
Imagine your repository is saved on a server that has a faulty hard drive, or even worse,
attackers get privileged access and modify the files in your repository with the intention
to make you restore malicious data:
echo "boom" >
/srv/restic-repo/index/de30f3231ca2e6a59af4aa84216dfe2ef7339c549dc11b09b84000997b13962
## 8

Trying to restore a snapshot which has been modified as shown above will yield an
error:
restic -r /srv/restic-repo --no-cache restore c23e491f --target /tmp/restore-work
## ...
Fatal: unable to load index de30f323: load <index/de30f3231c>: invalid data returned

In order to detect these things before they become a problem, it’s a good idea to
regularly use the
check command to test whether your repository is healthy and
consistent, and that your precious backup data is unharmed. There are two types of
checks that can be performed:
● Structural consistency and integrity, e.g. snapshots, trees and pack files
## (default)
● Integrity of the actual data that you backed up (enabled with flags, see below)
To verify the structure of the repository, issue the check command. If the repository is
damaged like in the example above,
check will detect this and yield the same error as
when you tried to restore:
restic -r /srv/restic-repo check
## ...

load indexes
error: error loading index
de30f3231ca2e6a59af4aa84216dfe2ef7339c549dc11b09b84000997b139628:
LoadRaw(<index/de30f3231c>): invalid data returned


The repository index is damaged and must be repaired. You must run `restic repair
index' to correct this.


Fatal: repository contains errors

## Warning
If check reports an error in the repository, then you must repair the repository. As long as
a repository is damaged, restoring some files or directories will fail. New snapshots are
not guaranteed to be restorable either.
For instructions how to repair a damaged repository, see the Troubleshooting section or
follow the instructions provided by the check command.
If the repository structure is intact, restic will show that no errors were found:
restic -r /src/restic-repo check
## ...
load indexes
check all packs
check snapshots, trees and blobs
no errors were found

By default, check creates a new temporary cache directory to verify that the data stored
in the repository is intact. To reuse the existing cache, you can use the
--with-cache flag.
If the cache directory is not explicitly set, then check creates its temporary cache
directory in the temporary directory, see Temporary files. Otherwise, the specified cache
directory is used, as described in Caching.

By default, the check command does not verify that the actual pack files on disk in the
repository are unmodified, because doing so requires reading a copy of every pack file
in the repository. To tell restic to also verify the integrity of the pack files in the
repository, use the
--read-data flag:
restic -r /srv/restic-repo check --read-data
## ...
load indexes
check all packs
check snapshots, trees and blobs
read all data
3 / 3 items
duration: 0:00
no errors were found

## Note
Since --read-data has to download all pack files in the repository, beware that it might
incur higher bandwidth costs than usual and also that it takes more time than the default
check.
Alternatively, use the --read-data-subset parameter to check only a subset of the
repository pack files at a time. It supports three ways to select a subset. One selects a
specific part of pack files, the second and third selects a random subset of the pack files
by the given percentage or size.
Use --read-data-subset=n/t to check a specific part of the repository pack files at a time.
The parameter takes two values,
n and t. When the check command runs, all pack files
in the repository are logically divided in
t (roughly equal) groups, and only files that
belong to group number
n are checked. For example, the following commands check all
repository pack files over 5 separate invocations:
restic -r /srv/restic-repo check --read-data-subset=1/5
restic -r /srv/restic-repo check --read-data-subset=2/5
restic -r /srv/restic-repo check --read-data-subset=3/5
restic -r /srv/restic-repo check --read-data-subset=4/5

restic -r /srv/restic-repo check --read-data-subset=5/5

Use --read-data-subset=x% to check a randomly chosen subset of the repository pack
files. It takes one parameter,
x, the percentage of pack files to check as an integer or
floating point number. This will not guarantee to cover all available pack files after
sufficient runs, but it is easy to automate checking a small subset of data after each
backup. For a floating point value the following command may be used:
restic -r /srv/restic-repo check --read-data-subset=2.5%

When checking bigger subsets you most likely want to specify the percentage as an
integer:
restic -r /srv/restic-repo check --read-data-subset=10%

Use --read-data-subset=nS to check a randomly chosen subset of the repository pack
files. It takes one parameter,
nS, where ‘n’ is a whole number representing file size and
‘S’ is the unit of file size (K/M/G/T) of pack files to check. Behind the scenes, the
specified size will be converted to percentage of the total repository size. The behaviour
of the check command following this conversion will be the same as the percentage
option above. For a file size value the following command may be used:
restic -r /srv/restic-repo check --read-data-subset=50M
restic -r /srv/restic-repo check --read-data-subset=10G

Upgrading the repository format version
Repositories created using earlier restic versions use an older repository format version
and have to be upgraded to allow using all new features. Upgrading must be done
explicitly as a newer repository version increases the minimum restic version required to

access the repository. For example the repository format version 2 is only readable
using restic 0.14.0 or newer.
Upgrading to repository version 2 is a two step process: first run migrate upgrade_repo_v2
which will check the repository integrity and then upgrade the repository version.
Repository problems must be corrected before the migration will be possible. After the
migration is complete, run
prune to compress the repository metadata. To limit the
amount of data rewritten in at once, you can use the
prune --max-repack-size size
parameter, see Customize pruning for more details.
File contents stored in the repository will not be rewritten, data from new backups will be
compressed. Over time more and more of the repository will be compressed. To speed
up this process and compress all not yet compressed data, you can run
prune
## --repack-uncompressed
. When you plan to create your backups with maximum
compression, you should also add the
--compression max flag to the prune command. For
already backed up data, the compression level cannot be changed later on.
## Tuning Backup Parameters
Restic offers a few parameters that allow tuning the backup. The default values should
work well in general although specific use cases can benefit from different non-default
values. As the restic commands evolve over time, the optimal value for each parameter
can also change across restic versions.
## Disabling Backup Progress Estimation
When you start a backup, restic will concurrently count the number of files and their total
size, which is used to estimate how long it will take. This will cause some extra I/O,
which can slow down backups of network file systems or FUSE mounts. To avoid this
overhead at the cost of not seeing a progress estimate, use the
--no-scan option of the
backup command which disables this file scanning.

## Backend Connections
Restic uses a global limit for the number of concurrent connections to a backend. This
limit can be configured using
-o <backend-name>.connections=5, for example for the REST
backend the parameter would be
-o rest.connections=5 or for the local backend -o
local.connections=2
. By default restic uses 5 connections for each backend, except for
the local backend which uses a limit of
- The defaults should work well in most cases.
For high-latency backends it can be beneficial to increase the number of connections.
Please be aware that this increases the resource consumption of restic and that a too
high connection count will degrade performance.
CPU Usage
By default, restic uses all available CPU cores. You can set the environment variable
GOMAXPROCS to limit the number of used CPU cores. For example to use a single
CPU core, use GOMAXPROCS=1. Limiting the number of usable CPU cores, can
slightly reduce the memory usage of restic.
## Compression
For a repository using at least repository format version 2, you can configure how data
is compressed with the option
--compression. It can be set to auto (the default, which will
compress very fast),
max (which will trade backup speed and CPU usage for slightly
better compression), or
off (which disables compression). Each setting is only applied
for the single run of restic. The option can also be set via the environment variable
## RESTIC_COMPRESSION.
## Data Verification
To prevent the upload of corrupted data to the repository, which can happen due to
hardware issues or software bugs, restic verifies that generated files can be decoded
and contain the correct data beforehand. This increases the CPU usage during

backups. If necessary, you can disable this verification using the --no-extra-verify
option of the
backup command. However, in this case you should verify the repository
integrity more actively using
restic check --read-data (or the similar --read-data-subset
option). Otherwise, data corruption due to hardware issues or software bugs might go
unnoticed.
## File Read Concurrency
When backing up files from fast storage like NVMe disks, it can be beneficial to increase
the read concurrency. This can increase the overall performance of the backup
operation by reading more files in parallel. You can specify the concurrency of file reads
with the
RESTIC_READ_CONCURRENCY environment variable or the --read-concurrency option of
the
backup command.
## Pack Size
In certain instances, such as very large repositories (in the TiB range) or very fast
upload connections, it is desirable to use larger pack sizes to reduce the number of files
in the repository and improve upload performance. Notable examples are OpenStack
Swift and some Google Drive Team accounts, where there are hard limits on the total
number of files. Larger pack sizes can also improve the backup speed for a repository
stored on a local HDD. This can be achieved by either using the
--pack-size option or
defining the
$RESTIC_PACK_SIZE environment variable. Restic currently defaults to a 16
MiB pack size.
The side effect of increasing the pack size is requiring more disk space for temporary
pack files created before uploading. The space must be available in the system default
temp directory, unless overwritten by setting the
$TMPDIR (except Windows) environment
variable (on Windows use
$TMP or $TEMP). In addition, depending on the backend the
memory usage can also increase by a similar amount. Restic requires temporary space
according to the pack size, multiplied by the number of backend connections plus one.
For example, if the backend uses 5 connections (the default for most backends), with a

target pack size of 64 MiB, you’ll need a minimum of 384 MiB of space in the temp
directory. A bit of tuning may be required to strike a balance between resource usage at
the backup client and the number of pack files in the repository.
Note that larger pack files increase the chance that the temporary pack files are written
to disk. An operating system usually caches file write operations in memory and writes
them to disk after a short delay. As larger pack files take longer to upload, this increases
the chance of these files being written to disk. This can increase disk wear for SSDs.
## Feature Flags
Feature flags allow disabling or enabling certain experimental restic features. The flags
can be specified via the
RESTIC_FEATURES environment variable. The variable expects a
comma-separated list of
key[=value],key2[=value2] pairs. The key is the name of a
feature flag. The value is optional and can contain either the value
true (default if
omitted) or
false. The list of currently available feature flags is shown by the features
command.
Restic will return an error if an invalid feature flag is specified. No longer relevant
feature flags may be removed in a future restic release. Thus, make sure to no longer
specify these flags.
A feature can either be in alpha, beta, stable or deprecated state.
● An _alpha_ feature is disabled by default and may change in arbitrary ways
between restic versions or be removed.
● A _beta_ feature is enabled by default, but still can change in minor ways or
be removed.
● A _stable_ feature is always enabled and cannot be disabled. This allows for
a transition period after which the flag will be removed in a future restic
version.

● A _deprecated_ feature is always disabled and cannot be enabled. The flag
will be removed in a future restic version.
Restoring from backup
Restoring from a snapshot
Restoring a snapshot is as easy as it sounds, just use the following command to restore
the contents of the latest snapshot to
## /tmp/restore-work:
restic -r /srv/restic-repo restore 79766175 --target /tmp/restore-work
enter password for repository:
restoring <Snapshot of [/home/user/work] at 2015-05-08 21:40:19.884408621 +0200 CEST>
to /tmp/restore-work


Use the word latest to restore the last backup. You can also combine latest with the
--host and --path filters to choose the last backup for a specific host, path or both.
restic -r /srv/restic-repo restore latest --target /tmp/restore-art --path "/home/art"
--host luigi
enter password for repository:
restoring <Snapshot of [/home/art] at 2015-05-08 21:45:17.884408621 +0200 CEST> to
## /tmp/restore-art


Use --exclude and --include to restrict the restore to a subset of files in the snapshot.
For example, to restore a single file:
restic -r /srv/restic-repo restore 79766175 --target /tmp/restore-work --include
## /work/foo
enter password for repository:
restoring <Snapshot of [/home/user/work] at 2015-05-08 21:40:19.884408621 +0200 CEST>
to /tmp/restore-work


This will restore the file foo to /tmp/restore-work/work/foo.

To only restore a specific subfolder, you can use the <snapshot>:<subfolder> syntax,
where
snapshot is the ID of a snapshot (or the string latest) and subfolder is a path
within the snapshot.
restic -r /srv/restic-repo restore 79766175:/work --target /tmp/restore-work --include
## /foo
enter password for repository:
restoring <Snapshot of [/home/user/work] at 2015-05-08 21:40:19.884408621 +0200 CEST>
to /tmp/restore-work


This will restore the file foo to /tmp/restore-work/foo.
You can use the command restic ls latest or restic find foo to find the path to the file
within the snapshot. This path you can then pass to
--include in verbatim to only restore
the single file or directory.
There are case insensitive variants of --exclude and --include called --iexclude and
--iinclude. These options will behave the same way but ignore the casing of paths.
There are also --include-file, --exclude-file, --iinclude-file and --iexclude-file flags
that read the include and exclude patterns from a file.
Restoring symbolic links on windows is only possible when the user has
SeCreateSymbolicLinkPrivilege privilege or is running as admin. This is a restriction of
windows not restic.
Restoring full security descriptors on Windows is only possible when the user has
SeRestorePrivilege, SeSecurityPrivilege and SeTakeOwnershipPrivilege privilege or is
running as admin. This is a restriction of Windows not restic. If either of these conditions
are not met, only the DACL will be restored.
By default, restic does not restore files as sparse. Use restore --sparse to enable the
creation of sparse files if supported by the filesystem. Then restic will restore long runs

of zero bytes as holes in the corresponding files. Reading from a hole returns the
original zero bytes, but it does not consume disk space. Note that the exact location of
the holes can differ from those in the original file, as their location is determined while
restoring and is not stored explicitly.
Restoring extended file attributes
By default, all extended attributes for files are restored.
Use only --exclude-xattr or --include-xattr to control which extended attributes are
restored for files in the snapshot. For example, to restore user and security
namespaced extended attributes for files:
restic -r /srv/restic-repo restore 79766175 --target /tmp/restore-work --include-xattr
user.* --include-xattr security.*
enter password for repository:
restoring <Snapshot of [/home/user/work] at 2015-05-08 21:40:19.884408621 +0200 CEST>
to /tmp/restore-work


Restoring in-place
## Note
Restoring data in-place can leave files in a partially restored state if the restore
operation is interrupted. To ensure you can revert back to the previous state, create a
current
backup before restoring a different snapshot.
By default, the restore command overwrites already existing files at the target directory.
This behavior can be configured via the
--overwrite option. The following values are
supported:

● --overwrite always (default): always overwrites already existing files. restore
will verify the existing file content and only restore mismatching parts to
minimize downloads. Updates the metadata of all files.
● --overwrite if-changed: like the previous case, but speeds up the file content
check by assuming that files with matching size and modification time (mtime)
are already up to date. In case of a mismatch, the full file content is verified.
Updates the metadata of all files.
● --overwrite if-newer: only overwrite existing files if the file in the snapshot has
a newer modification time (mtime).
● --overwrite never: never overwrite existing files.
Delete files not in snapshot
When restoring into a directory that already contains files, it can be useful to remove all
files that do not exist in the snapshot. For this, pass the
--delete option to the restore
command. The command will then delete all files from the target directory that do not
exist in the snapshot.
The --delete option also allows overwriting a non-empty directory if the snapshot
contains a file with the same name.
## Warning
Always use the --dry-run -vv option to verify what would be deleted before running the
actual command.
When specifying --include or --exclude options, only files or directories matched by
those options will be deleted. For example, the command
restic -r /srv/restic-repo
restore 79766175:/work --target /tmp/restore-work --include /foo --delete
would only
delete files within
## /tmp/restore-work/foo.

When using --target / --delete then the restore command only works if either an
--include or --exclude option is also specified. This ensures that one cannot accidentally
delete the whole system.
Dry run
As restore operations can take a long time, it can be useful to perform a dry-run to see
what would be restored without having to run the full restore operation. The restore
command supports the
--dry-run option and prints information about the restored files
when specifying
## --verbose=2.
restic restore --target /tmp/restore-work --dry-run --verbose=2 latest

unchanged /restic/internal/walker/walker.go with size 2.812 KiB
updated   /restic/internal/walker/walker_test.go with size 11.143 KiB
restored  /restic/restic with size 35.318 MiB
restored  /restic
## [...]
Summary: Restored 9072 files/dirs (153.597 MiB) in 0:00

Files with already up to date content are reported as unchanged. Files whose content was
modified are
updated and files that are new are shown as restored. Directories and other
file types like symlinks are always reported as
restored.
To reliably determine which files would be updated, a dry-run also verifies the content of
already existing files according to the specified overwrite behavior. To skip these checks
either specify
--overwrite never or specify a non-existing --target directory.
Restore using mount
Browsing your backup as a regular file system is also very easy. First, create a mount
point such as
/mnt/restic and then use the following command to serve the repository
with FUSE:
mkdir /mnt/restic
restic -r /srv/restic-repo mount /mnt/restic

enter password for repository:
Now serving /srv/restic-repo at /mnt/restic
Use another terminal or tool to browse the contents of this folder.
When finished, quit with Ctrl-c here or umount the mountpoint.

Mounting repositories via FUSE is only possible on Linux, macOS and FreeBSD. On
Linux, the
fuse kernel module needs to be loaded and the fusermount command needs to
be in the PATH. On macOS, you need FUSE-T or FUSE for macOS. On FreeBSD, you
may need to install FUSE and load the kernel module (kldload fuse).
Restic supports storage and preservation of hard links. However, since hard links exist
in the scope of a filesystem by definition, restoring hard links from a fuse mount should
be done by a program that preserves hard links. A program that does so is
rsync, used
with the option
## --hard-links.
## Note
restic mount is mostly useful if you want to restore just a few files out of a snapshot, or
to check which files are contained in a snapshot. To restore many files or a whole
snapshot,
restic restore is the best alternative, often it is significantly faster.
Printing files to stdout
Sometimes it’s helpful to print files to stdout so that other programs can read the data
directly. This can be achieved by using the dump command, like this:
restic -r /srv/restic-repo dump latest production.sql | mysql

If you have saved multiple different things into the same repo, the latest snapshot may
not be the right one. For example, consider the following snapshots in a repository:
restic -r /srv/restic-repo snapshots
ID        Date                 Host        Tags        Directory

## ----------------------------------------------------------------------
562bfc5e  2018-07-14 20:18:01  mopped                  /home/user/file1
bbacb625  2018-07-14 20:18:07  mopped                  /home/other/work
e922c858  2018-07-14 20:18:10  mopped                  /home/other/work
098db9d5  2018-07-14 20:18:13  mopped                  /production.sql
b62f46ec  2018-07-14 20:18:16  mopped                  /home/user/file1
1541acae  2018-07-14 20:18:18  mopped                  /home/other/work
## ----------------------------------------------------------------------

Here, restic would resolve latest to the snapshot 1541acae, which does not contain the
file we’d like to print at all (
production.sql). In this case, you can pass restic the
snapshot ID of the snapshot you like to restore:
restic -r /srv/restic-repo dump 098db9d5 production.sql | mysql

Or you can pass restic a path that should be used for selecting the latest snapshot. The
path must match the patch printed in the “Directory” column, e.g.:
restic -r /srv/restic-repo dump --path /production.sql latest production.sql | mysql

It is also possible to dump the contents of a whole folder structure to stdout. To retain the
information about the files and folders Restic will output the contents in the tar (default)
or zip format:
restic -r /srv/restic-repo dump latest /home/other/work > restore.tar

restic -r /srv/restic-repo dump -a zip latest /home/other/work > restore.zip

The folder content is then contained at /home/other/work within the archive. To include
the folder content at the root of the archive, you can use the
## <snapshot>:<subfolder>
syntax:
restic -r /srv/restic-repo dump latest:/home/other/work / > restore.tar


It is also possible to dump the contents of a selected snapshot and folder structure to a
file using the
--target flag.
restic -r /srv/restic-repo dump latest / --target /home/linux.user/output.tar -a tar

Removing backup snapshots
All backup space is finite, so restic allows removing old snapshots. This can be done
either manually (by specifying a snapshot ID to remove) or by using a policy that
describes which snapshots to forget. For all remove operations, two commands need to
be called in sequence:
forget to remove snapshots, and prune to remove the remaining
data that was referenced only by the removed snapshots. The latter can be automated
with the
--prune option of forget, which runs prune automatically if any snapshots were
actually removed.
Pruning snapshots can be a time-consuming process, depending on the number of
snapshots and data to process. During a prune operation, the repository is locked and
backups cannot be completed. Please plan your pruning so that there’s time to
complete it and it doesn’t interfere with regular backup runs.
It is advisable to run restic check after pruning, to make sure you are alerted, should the
internal data structures of the repository be damaged.
Remove a single snapshot
The command snapshots can be used to list all snapshots in a repository like this:
restic -r /srv/restic-repo snapshots
enter password for repository:
ID        Date                 Host      Tags  Directory
## ----------------------------------------------------------------------
40dc1520  2015-05-08 21:38:30  kasimir         /home/user/work
79766175  2015-05-08 21:40:19  kasimir         /home/user/work
bdbd3439  2015-05-08 21:45:17  luigi           /home/art

590c8fc8  2015-05-08 21:47:38  kazik           /srv
9f0bc19e  2015-05-08 21:46:11  luigi           /srv

In order to remove the snapshot of /home/art, use the forget command and specify the
snapshot ID on the command line:
restic -r /srv/restic-repo forget bdbd3439
enter password for repository:
removed snapshot bdbd3439

Afterwards this snapshot is removed:
restic -r /srv/restic-repo snapshots
enter password for repository:
ID        Date                 Host     Tags  Directory
## ----------------------------------------------------------------------
40dc1520  2015-05-08 21:38:30  kasimir        /home/user/work
79766175  2015-05-08 21:40:19  kasimir        /home/user/work
590c8fc8  2015-05-08 21:47:38  kazik          /srv
9f0bc19e  2015-05-08 21:46:11  luigi          /srv

But the data that was referenced by files in this snapshot is still stored in the repository.
To cleanup unreferenced data, the
prune command must be run:
restic -r /srv/restic-repo prune
enter password for repository:
repository 33002c5e opened successfully
loading all snapshots...
loading indexes...
finding data that is still in use for 4 snapshots
4 / 4 snapshots
searching used packs...
collecting packs for deletion and repacking
5 / 5 packs processed

to repack:            69 blobs / 1.078 MiB
this removes:         67 blobs / 1.047 MiB
to delete:             7 blobs / 25.726 KiB
total prune:          74 blobs / 1.072 MiB
remaining:            16 blobs / 38.003 KiB
unused size after prune: 0 B (0.00% of remaining size)

repacking packs
2 / 2 packs repacked

rebuilding index
3 / 3 packs processed
deleting obsolete index files
3 / 3 files deleted
removing 3 old packs
3 / 3 files deleted
done

Afterwards the repository is smaller.
You can automate this two-step process by using the --prune switch to forget:
restic forget --keep-last 1 --prune
snapshots for host mopped, directories /home/user/work:

keep 1 snapshots:
ID        Date                 Host        Tags        Directory
## ----------------------------------------------------------------------
4bba301e  2017-02-21 10:49:18  mopped                  /home/user/work

remove 1 snapshots:
ID        Date                 Host        Tags        Directory
## ----------------------------------------------------------------------
8c02b94b  2017-02-21 10:48:33  mopped                  /home/user/work

1 snapshots have been removed, running prune
loading all snapshots...
loading indexes...
finding data that is still in use for 1 snapshots
1 / 1 snapshots
searching used packs...
collecting packs for deletion and repacking
5 / 5 packs processed

to repack:           69 blobs / 1.078 MiB
this removes         67 blobs / 1.047 MiB
to delete:            7 blobs / 25.726 KiB
total prune:         74 blobs / 1.072 MiB
remaining:           16 blobs / 38.003 KiB
unused size after prune: 0 B (0.00% of remaining size)

repacking packs
2 / 2 packs repacked
rebuilding index
3 / 3 packs processed
deleting obsolete index files
3 / 3 files deleted
removing 3 old packs
3 / 3 files deleted
done


Removing snapshots according to a policy
Removing snapshots manually is tedious and error-prone, therefore restic allows
specifying a policy (one or more
--keep-* options) for which snapshots to keep. You can
for example define how many hourly, daily, weekly, monthly and yearly snapshots to
keep, and any other snapshots will be removed.
## Warning
If you use an append-only repository with policy-based snapshot removal, some
security considerations are important. Please refer to the section below for more
information.
## Note
You can always use the --dry-run option of the forget command, which instructs restic
to not remove anything but instead just print what actions would be performed.
The forget command accepts the following policy options:
● --keep-last n keep the n last (most recent) snapshots.
● --keep-hourly n for the last n hours which have one or more snapshots, keep
only the most recent one for each hour.
● --keep-daily n for the last n days which have one or more snapshots, keep
only the most recent one for each day.
● --keep-weekly n for the last n weeks which have one or more snapshots, keep
only the most recent one for each week.
● --keep-monthly n for the last n months which have one or more snapshots,
keep only the most recent one for each month.

● --keep-yearly n for the last n years which have one or more snapshots, keep
only the most recent one for each year.
● --keep-tag keep all snapshots which have all tags specified by this option (can
be specified multiple times). The
forget command will exit with an error if all
snapshots in a snapshot group would be removed as none of them have the
specified tags.
● --keep-within duration keep all snapshots having a timestamp within the
specified duration of the latest snapshot, where
duration is a number of years,
months, days, and hours. E.g.
2y5m7d3h will keep all snapshots made in the
two years, five months, seven days and three hours before the latest (most
recent) snapshot.
● --keep-within-hourly duration keep all hourly snapshots made within the
specified duration of the latest snapshot. The
duration is specified in the same
way as for
--keep-within and the method for determining hourly snapshots is
the same as for
## --keep-hourly.
● --keep-within-daily duration keep all daily snapshots made within the
specified duration of the latest snapshot.
● --keep-within-weekly duration keep all weekly snapshots made within the
specified duration of the latest snapshot.
● --keep-within-monthly duration keep all monthly snapshots made within the
specified duration of the latest snapshot.
● --keep-within-yearly duration keep all yearly snapshots made within the
specified duration of the latest snapshot.
## Note
All calendar related options (--keep-{hourly,daily,...}) work on natural time boundaries
and not relative to when you run
forget. Weeks are Monday 00:00 to Sunday 23:59,
days 00:00 to 23:59, hours :00 to :59, etc. They also only count hours/days/weeks/etc
which have one or more snapshots. A value of
unlimited will be interpreted as “forever”,
i.e. “keep all”.

## Note
All duration related options (--keep-{within-,}*) ignore snapshots with a timestamp in
the future (relative to when the
forget command is run) and these snapshots will hence
not be removed.
## Note
If there are not enough snapshots to keep one for each duration related
--keep-{within-,}* option, the oldest snapshot is kept additionally and marked as oldest
in the output (e.g.
oldest hourly snapshot).
## Note
Specifying --keep-tag '' will match untagged snapshots only.
When forget is run with a policy, restic first loads the list of all snapshots and groups
them by their host name and paths. The grouping options can be set with
## --group-by,
e.g. using
--group-by paths,tags to instead group snapshots by paths and tags. The
policy is then applied to each group of snapshots individually. This is a safety feature to
prevent accidental removal of unrelated backup sets. To disable grouping and apply the
policy to all snapshots regardless of their host, paths and tags, use
## --group-by '' (that
is, an empty value to
--group-by). Note that one would normally set the --group-by option
for the
backup command to the same value.
Additionally, you can restrict the policy to only process snapshots which have a
particular hostname with the
--host parameter, or tags with the --tag option. When
multiple tags are specified, only the snapshots which have all the tags are considered.
For example, the following command removes all but the latest snapshot of all
snapshots that have the tag
foo:

restic forget --tag foo --keep-last 1

This command removes all but the last snapshot of all snapshots that have either the
foo or bar tag set:
restic forget --tag foo --tag bar --keep-last 1

To only keep the last snapshot of all snapshots with both the tag foo and bar set use:
restic forget --tag foo,bar --keep-last 1

To ensure only untagged snapshots are considered, specify the empty string ‘’ as the
tag.
restic forget --tag '' --keep-last 1

Let’s look at a simple example: Suppose you have only made one backup every Sunday
for 12 weeks:
restic snapshots
repository f00c6e2a opened successfully
ID        Time                 Host        Tags        Paths
## ---------------------------------------------------------------
0a1f9759  2019-09-01 11:00:00  mopped                  /home/user/work
46cfe4d5  2019-09-08 11:00:00  mopped                  /home/user/work
f6b1f037  2019-09-15 11:00:00  mopped                  /home/user/work
eb430a5d  2019-09-22 11:00:00  mopped                  /home/user/work
8cf1cb9a  2019-09-29 11:00:00  mopped                  /home/user/work
5d33b116  2019-10-06 11:00:00  mopped                  /home/user/work
b9553125  2019-10-13 11:00:00  mopped                  /home/user/work
e1a7b58b  2019-10-20 11:00:00  mopped                  /home/user/work
8f8018c0  2019-10-27 11:00:00  mopped                  /home/user/work
59403279  2019-11-03 11:00:00  mopped                  /home/user/work
dfee9fb4  2019-11-10 11:00:00  mopped                  /home/user/work
e1ae2f40  2019-11-17 11:00:00  mopped                  /home/user/work
## ---------------------------------------------------------------
12 snapshots


Then forget --keep-daily 4 will keep the last four snapshots, for the last four Sundays,
and remove the other snapshots:
restic forget --keep-daily 4 --dry-run
repository f00c6e2a opened successfully
Applying Policy: keep the last 4 daily snapshots
keep 4 snapshots:
ID        Time                 Host        Tags        Reasons         Paths
## -------------------------------------------------------------------------------
8f8018c0  2019-10-27 11:00:00  mopped                  daily snapshot  /home/user/work
59403279  2019-11-03 11:00:00  mopped                  daily snapshot  /home/user/work
dfee9fb4  2019-11-10 11:00:00  mopped                  daily snapshot  /home/user/work
e1ae2f40  2019-11-17 11:00:00  mopped                  daily snapshot  /home/user/work
## -------------------------------------------------------------------------------
4 snapshots

remove 8 snapshots:
ID        Time                 Host        Tags        Paths
## ---------------------------------------------------------------
0a1f9759  2019-09-01 11:00:00  mopped                  /home/user/work
46cfe4d5  2019-09-08 11:00:00  mopped                  /home/user/work
f6b1f037  2019-09-15 11:00:00  mopped                  /home/user/work
eb430a5d  2019-09-22 11:00:00  mopped                  /home/user/work
8cf1cb9a  2019-09-29 11:00:00  mopped                  /home/user/work
5d33b116  2019-10-06 11:00:00  mopped                  /home/user/work
b9553125  2019-10-13 11:00:00  mopped                  /home/user/work
e1a7b58b  2019-10-20 11:00:00  mopped                  /home/user/work
## ---------------------------------------------------------------
8 snapshots

The processed snapshots are evaluated against all --keep-* options but a snapshot only
need to match a single option to be kept (the results are ORed). This means that the
most recent snapshot on a Sunday would match both hourly, daily and weekly
## --keep-*
options, and possibly more depending on calendar.
For example, suppose you make one backup every day for 100 years. Then forget
## --keep-daily 7 --keep-weekly 5 --keep-monthly 12 --keep-yearly 75
would keep the most
recent 7 daily snapshots and 4 last-day-of-the-week ones (since the 7 dailies already
include 1 weekly). Additionally, 12 or 11 last-day-of-the-month snapshots will be kept
(depending on whether one of them ends up being the same as a daily or weekly). And
finally 75 or 74 last-day-of-the-year snapshots are kept, depending on whether one of

them ends up being the same as an already kept snapshot. All other snapshots are
removed.
You might want to maintain the same policy as in the example above, but have irregular
backups. For example, the 7 snapshots specified with
--keep-daily 7 might be spread
over a longer period. If what you want is to keep daily snapshots for the last week,
weekly for the last month, monthly for the last year and yearly for the last 75 years, you
can instead specify
forget --keep-within-daily 7d --keep-within-weekly 1m
## --keep-within-monthly 1y --keep-within-yearly 75y
(note that 1w is not a recognized
duration, so you will have to specify 7d instead).
Removing all snapshots
For safety reasons, restic refuses to act on an “empty” policy. For example, if one were
to specify
--keep-last 0 to forget all snapshots in the repository, restic will respond that
no snapshots will be removed. To delete all snapshots, use
--keep-last 1 and then
finally remove the last snapshot manually (by passing the ID to
forget).
Since restic 0.17.0, it is possible to delete all snapshots for a specific host, tag or path
using the
--unsafe-allow-remove-all option. The option must always be combined with a
snapshot filter (by host, path or tag). For example the command
forget --tag example
## --unsafe-allow-remove-all
removes all snapshots with tag example.
Security considerations in append-only mode
## Note
TL;DR: With append-only repositories, one should specifically use the --keep-within
option of the
forget command when removing snapshots.
To prevent a compromised backup client from deleting its backups (for example due to a
ransomware infection), a repository service/backend can serve the repository in a

so-called append-only mode. This means that the repository is served in such a way
that it can only be written to and read from, while delete and overwrite operations are
denied. Restic’s rest-server features an append-only mode, but few other standard
backends do. To support append-only with such backends, one can use rclone as a
complement in between the backup client and the backend service.
To remove snapshots and recover the corresponding disk space, the forget and prune
commands require full read, write and delete access to the repository. If an attacker has
this, the protection offered by append-only mode is naturally void. The usual and
recommended setup with append-only repositories is therefore to use a separate and
well-secured client whenever full access to the repository is needed, e.g. for
administrative tasks such as running
forget, prune and other maintenance commands.
However, even with append-only mode active and a separate, well-secured client used
for administrative tasks, an attacker who is able to add garbage snapshots to the
repository could bring the snapshot list into a state where all the legitimate snapshots
risk being deleted by an unsuspecting administrator that runs the
forget command with
certain
--keep-* options, leaving only the attacker’s useless snapshots.
For example, if the forget policy is to keep three weekly snapshots, and the attacker
adds an empty snapshot for each of the last three weeks, all with a timestamp (see the
backup command’s --time option) slightly more recent than the existing snapshots (but
still within the target week), then the next time the repository administrator (or a
scheduled job) runs the
forget command with this policy, the legitimate snapshots will
be removed (since the policy will keep only the most recent snapshot within each week).
Even without running
prune, recovering data would be messy and some metadata lost.
To avoid this, forget policies applied to append-only repositories should use the
--keep-within option, as this will keep not only the attacker’s snapshots but also the
legitimate ones. Assuming the system time is correctly set when
forget runs, this will
allow the administrator to notice problems with the backup or the compromised host
(e.g. by seeing more snapshots than usual or snapshots with suspicious timestamps).

This is, of course, limited to the specified duration: if forget --keep-within 7d is run 8
days after the last good snapshot, then the attacker can still use that opportunity to
remove all legitimate snapshots.
Customize pruning
To understand the custom options, we first explain how the pruning process works:
- All snapshots and directories within snapshots are scanned to determine
which data is still in use.
- For all files in the repository, restic finds out if the file is fully used, partly used
or completely unused.
- Completely unused files are marked for deletion. Fully used files are kept. A
partially used file is either kept or marked for repacking depending on user
options.
Note that for repacking, restic must download the file from the repository
storage and re-upload the needed data in the repository. This can be very
time-consuming for remote repositories.
- After deciding what to do, prune will actually perform the repack, modify the
index according to the changes and delete the obsolete files.
The prune command accepts the following options:
● --max-unused limit allow unused data up to the specified limit within the
repository. This allows restic to keep partly used files instead of repacking
them.
The limit can be specified in several ways:
○ As an absolute size (e.g. 200M). If you want to minimize the
space used by your repository, pass
0 to this option.
○ As a size relative to the total repository size (e.g. 10%). This
means that after prune, at most
10% of the total data stored in the

repository may be unused data. If the repository after prune has
a size of 500MB, then at most 50MB may be unused.
○ If the string unlimited is passed, there is no limit for partly
unused files. This means that as long as some data is still used
within a file stored in the repo, restic will just leave it there. Use
this if you want to minimize the time and bandwidth used by the
prune operation. Note that metadata will still be repacked.
● Restic tries to repack as little data as possible while still ensuring this limit for
unused data. The default value is 5%.
● --max-repack-size size if set limits the total size of files to repack. As prune first
stores all repacked files and deletes the obsolete files at the end, this option
might be handy if you expect many files to be repacked and fear to run low on
storage.
● --repack-cacheable-only if set to true only files which contain metadata and
would be stored in the cache are repacked. Other pack files are not repacked
if this option is set. This allows a very fast repacking using only cached data.
It can, however, imply that the unused data in your repository exceeds the
value given by
--max-unused. The default value is false.
● --repack-small if set will repack pack files below 80% of target pack size. The
default value is false.
● --repack-smaller-than will repack all packfiles below the size of
--repack-smaller-than. This allows repacking packfiles that initially came from
a repository with a smaller
--pack-size to be compacted into larger packfiles.
● --dry-run only show what prune would do.
● --verbose increased verbosity shows additional statistics for prune.
Recovering from “no free space” errors
In some cases when a repository has grown large enough to fill up all disk space or the
allocated quota, then
prune might fail to free space. prune works in such a way that a

repository remains usable no matter at which point the command is interrupted.
However, this also means that
prune requires some scratch space to work.
In most cases it is sufficient to instruct prune to use as little scratch space as possible by
running it as
prune --max-repack-size 0. Note that for restic versions before 0.13.0 prune
## --max-repack-size 1
must be used. Obviously, this can only work if several snapshots
have been removed using
forget before. This then allows the prune command to actually
remove data from the repository. If the command succeeds, but there is still little free
space, then remove a few more snapshots and run
prune again.
If prune fails to complete, then prune --unsafe-recover-no-free-space SOME-ID is available
as a method of last resort. It allows prune to work with little to no free space. However, a
failed
prune run can cause the repository to become temporarily unusable. Therefore,
make sure that you have a stable connection to the repository storage, before running
this command. In case the command fails, it may become necessary to manually
remove all files from the index/ folder of the repository and run repair index afterwards.
To prevent accidental usages of the --unsafe-recover-no-free-space option it is
necessary to first run
prune --unsafe-recover-no-free-space SOME-ID and then replace
SOME-ID with the requested ID.
## Encryption
“The design might not be perfect, but it’s good. Encryption is a first-class feature, the
implementation looks sane and I guess the deduplication trade-off is worth it. So... I’m
going to use restic for my personal backups.” Filippo Valsorda
Manage repository keys

The key command allows you to set multiple access keys or passwords per repository.
In fact, you can use the
list, add, remove, and passwd (changes a password)
sub-commands to manage these keys very precisely:
restic -r /srv/restic-repo key list
enter password for repository:
ID          User        Host        Created
## ----------------------------------------------------------------------
*eb78040b    username    kasimir   2015-08-12 13:29:57

restic -r /srv/restic-repo key add
enter password for repository:
enter password for new key:
enter password again:
saved new key as <Key of username@kasimir, created on 2015-08-12 13:35:05.316831933
## +0200 CEST>


restic -r /srv/restic-repo key list
enter password for repository:
ID          User        Host        Created
## ----------------------------------------------------------------------
5c657874    username    kasimir   2015-08-12 13:35:05
*eb78040b    username    kasimir   2015-08-12 13:29:57

Note that the currently used key is indicated by an asterisk (*).
## Scripting
This is a list of how certain tasks may be accomplished when you use restic via scripts.
Check if a repository is already initialized
You may find a need to check if a repository is already initialized, perhaps to prevent
your script from trying to initialize a repository multiple times (the
init command
contains a check to prevent overwriting existing repositories). The command
cat config
may be used for this purpose:
restic -r /srv/restic-repo cat config
Fatal: repository does not exist: unable to open config file: stat
/srv/restic-repo/config: no such file or directory

Is there a repository at the following location?

## /srv/restic-repo

If a repository does not exist, restic (since 0.17.0) will return exit code 10 and print a
corresponding error message. Older versions return exit code
- Note that restic will
also return exit code
1 if a different error is encountered (e.g.: incorrect password to cat
config
) and it may print a different error message. If there are no errors, restic will return
a zero exit code and print the repository metadata.
Exit codes
Restic commands return an exit code that signals whether the command was
successful. The following table provides a general description, see the help of each
command for a more specific description.
## Warning
New exit codes will be added over time. If an unknown exit code is returned, then it
MUST be treated as a command failure.
0 Command was successful
## 1
Command failed, see command help for more
details
2 Go runtime error

## 3
backup
command could not read some source data
10 Repository does not exist (since restic 0.17.0)
11 Failed to lock repository (since restic 0.17.0)
12 Wrong password (since restic 0.17.1)
130 Restic was interrupted using SIGINT or SIGSTOP
JSON output
Restic outputs JSON data to stdout if requested with the --json flag. The structure of
that data varies depending on the circumstance. The JSON output of most restic
commands are documented here.
## Note
Not all commands support JSON output. If a command does not support JSON output,
feel free to submit a pull request!
## Warning

We try to keep the JSON output backwards compatible. However, new message types
or fields may be added at any time. Similarly, enum-like fields for which a fixed list of
allowed values is documented may be extended at any time.
Exit errors
Fatal errors will result in a final JSON message on stderr before the process exits. It will
hold the error message and the exit code.
## Note
Some errors cannot be caught and reported this way, such as Go runtime errors or
command line parsing errors.
message_type
Always “exit_error” string
code
Exit code (see above
chart)
int
message
Error message string
Output formats
Commands print their main JSON output on stdout. The generated JSON output uses
one of the following two formats.
## Note

Not all messages and errors have been converted to JSON yet. Feel free to submit a
pull request!
The datatypes specified in the following sections roughly correspond to the underlying
Go types and are mapped to the JSON types as follows:
● int32, int64, uint32, uint64 and float64 are encoded as number.
● bool and string correspond to the respective types.
● [] in front of a type indicates that the field is an array of the respective type.
● time.Time is encoded as a string in RFC3339 format.
● os.FileMode is encoded as an uint32.
If a field contains a default value like 0 or "", it may be omitted from the JSON output.
Single JSON document
Several commands output a single JSON document that can be parsed in its entirety.
Depending on the command, the output consists of either a single or multiple lines.
JSON lines
Several commands, in particular long running ones or those that generate a large
output, use a format also known as JSON lines. It consists of a stream of new-line
separated JSON messages. You can determine the nature of the message using the
message_type field.
backup
The backup command uses the JSON lines format with the following message types.
## Status

message_type
Always “status” string
seconds_elapsed
Time since backup started uint64
seconds_remaining
Estimated time remaining uint64
percent_done
Fraction of data backed up
## (bytes_done/total_bytes)
float6
## 4
total_files
Total number of files detected uint64
files_done
Files completed (backed up to repo) uint64
total_bytes
Total number of bytes in backup set uint64
bytes_done
Number of bytes completed (backed up to repo) uint64
error_count
Number of errors uint64
current_files
List of files currently being backed up []string

## Error
These errors are printed on stderr.
message_type
Always “error” string
error.message
Error message string
during
What restic was trying to do string
item
Usually, the path of the problematic
file
string
## Verbose Status
Verbose status provides details about the progress, including details about backed up
files.
message_type
Always “verbose_status” string
action
Either “new”, “unchanged”, “modified” or
## “scan_finished”
string
item
The item in question string

duration
How long it took, in seconds
float6
## 4
data_size
How big the item is uint64
data_size_in_repo
How big the item is in the repository uint64
metadata_size
How big the metadata is uint64
metadata_size_in_rep
o
How big the metadata is in the repository uint64
total_files
Total number of files uint64
## Summary
Summary is the last output line in a successful backup.
message_type
Always “summary” string
dry_run
Whether the backup was a dry run bool

files_new
Number of new files uint64
files_changed
Number of files that changed uint64
files_unmodified
Number of files that did not change uint64
dirs_new
Number of new directories uint64
dirs_changed
Number of directories that changed uint64
dirs_unmodified
Number of directories that did not change uint64
data_blobs
Number of data blobs added int64
tree_blobs
Number of tree blobs added int64
data_added
Amount of (uncompressed) data added, in bytes uint64
data_added_packe
d
Amount of data added (after compression), in bytes uint64

total_files_proc
essed
Total number of files processed uint64
total_bytes_proc
essed
Total number of bytes processed uint64
backup_start
Time at which the backup was started
time.Ti
me
backup_end
Time at which the backup was completed
time.Ti
me
total_duration
Total time it took for the operation to complete float64
snapshot_id
ID of the new snapshot. Field is omitted if snapshot
creation was skipped
string
cat
The cat command returns data about various objects in the repository, which are stored
in JSON form. Specifying
--json or --quiet will suppress any non-JSON messages the
command generates.
check
The check command uses the JSON lines format with the following message types.
## Status

message_type
## Always “summary”
stri
ng
num_errors
Number of errors
int
## 64
broken_packs
Run “restic repair packs ID...” and “restic repair snapshots
–forget” to remove damaged files
## []st
rin
g
suggest_repai
r_index
Run “restic repair index”
bo
ol
suggest_prune
Run “restic prune”
bo
ol
## Error
These errors are printed on stderr.
message_typ
e
## Always “error”
strin
g
message
Error message. May change in arbitrary ways across restic
versions.
strin
g
diff

The diff command uses the JSON lines format with the following message types.
change
me
ss
ag
e_
ty
pe
## Always “change”
s
t
r
i
n
g
pa
th
Path that has changed
s
t
r
i
n
g
mo
di
fi
er
Type of change, a concatenation of the following characters: “+” = added, “-” =
removed, “T” = entry type changed, “M” = file content changed, “U” = metadata
changed, “?” = bitrot detected
s
t
r
i
n
g
statistics
message_type
Always “statistics” string
source_snapshot
ID of first snapshot string

target_snapshot
ID of second snapshot string
changed_files
Number of changed
files
int64
added
Added items
DiffStat
object
removed
Removed items
DiffStat
object
DiffStat object
files
Number of changed files int64
dirs
Number of changed directories int64
others
Number of changed other directory
entries
int64
data_blobs
Number of data blobs int64

tree_blobs
Number of tree blobs int64
bytes
Number of bytes uint64
find
The find command outputs a single JSON document containing an array of JSON
objects with matches for your search term. These matches are organized by snapshot.
If the --blob or --tree option is passed, then the output is an array of Blob objects.
hits
Number of matches in the
snapshot
uint64
snapshot
ID of the snapshot string
matches
Details of a match
## [] Match
object
Match object
path
Object path string
permissions
UNIX permissions string

name
Object name string
type
Object type e.g. file, dir, etc... string
atime
Access time time.Time
mtime
Modification time time.Time
ctime
Change time time.Time
user
Name of owner string
group
Name of group string
inode
Inode number uint64
mode
UNIX file mode, shorthand of
permissions
os.FileMod
e

device_id
OS specific device identifier uint64
links
Number of hardlinks uint64
link_target
Target of a symlink string
uid
ID of owner uint32
gid
ID of group uint32
size
Size of object in bytes uint64
Blob objects
object_type
Either “blob” or “tree” string
id
ID of found blob string
path
Path in snapshot string

parent_tree
Parent tree blob, only set for type
## “blob”
string
snapshot
Snapshot ID string
time
Snapshot timestamp
time.Tim
e
forget
The forget command prints a single JSON document containing an array of
ForgetGroups. If specific snapshot IDs are specified, then no output is generated.
The prune command does not yet support JSON such that forget --prune results in a
mix of JSON and text output.
ForgetGroup
tags
Tags identifying the snapshot group []string
host
Host identifying the snapshot group string
paths
Paths identifying the snapshot group []string

keep
Array of Snapshot that are kept [] Snapshot object
remove
Array of Snapshot that were removed [] Snapshot object
reason
s
Array of KeepReason objects describing why a
snapshot is kept
[] KeepReason
object
Snapshot object
time
Timestamp of when the backup was started time.Time
parent
ID of the parent snapshot string
tree
ID of the root tree blob string
paths
List of paths included in the backup []string
hostname
Hostname of the backed up machine string
username
Username the backup command was run as string

uid
ID of owner uint32
gid
ID of group uint32
excludes
List of paths and globs excluded from the
backup
## []string
tags
List of tags for the snapshot in question []string
program_versi
on
restic version used to create snapshot string
summary
Snapshot statistics
SnapshotSummary
object
id
Snapshot ID string
short_id
Snapshot ID, short form (deprecated) string
KeepReason object

snapshot
Snapshot described by this object
## Snapshot
object
matches
Array containing descriptions of the matching
criteria
## []string
init
The init command uses the JSON lines format, but only outputs a single message.
message_type
Always “initialized” string
id
ID of the created
repository
string
repository
URL of the repository string
key list
The key list command returns an array of objects with the following structure.
current
Is currently used key? bool
id
Unique key ID string

userName
User who created it string
hostName
Name of machine it was created
on
string
created
Timestamp when it was created
local
time.Time
ls
The ls command uses the JSON lines format with the following message types. As an
exception, the
struct_type field is used to determine the message type.
snapshot
message_type
Always “snapshot” string
struct_type
Always “snapshot” (deprecated) string
time
Timestamp of when the backup was started time.Time
parent
ID of the parent snapshot string

tree
ID of the root tree blob string
paths
List of paths included in the backup []string
hostname
Hostname of the backed up machine string
username
Username the backup command was run as string
uid
ID of owner uint32
gid
ID of group uint32
excludes
List of paths and globs excluded from the
backup
## []string
tags
List of tags for the snapshot in question []string
program_versi
on
restic version used to create snapshot string

summary
Snapshot statistics
SnapshotSummary
object
id
Snapshot ID string
short_id
Snapshot ID, short form (deprecated) string
node
message_type
Always “node” string
struct_type
## Always “node”
## (deprecated)
string
name
Node name string
type
Node type string
path
Node path string
uid
UID of node uint32

gid
GID of node uint32
size
Size in bytes uint64
mode
Node mode
os.FileMod
e
permissions
Node mode as string string
atime
Node access time time.Time
mtime
Node modification time time.Time
ctime
Node creation time time.Time
inode
Inode number of node uint64
restore
The restore command uses the JSON lines format with the following message types.
## Status

message_type
Always “status” string
seconds_elapsed
Time since restore started uint64
percent_done
Percentage of data restored
## (bytes_restored/total_bytes)
float6
## 4
total_files
Total number of files detected uint64
files_restored
Files restored uint64
files_skipped
Files skipped due to overwrite setting uint64
files_deleted
Files deleted uint64
total_bytes
Total number of bytes in restore set uint64
bytes_restored
Number of bytes restored uint64
bytes_skipped
Total size of skipped files uint64

## Error
These errors are printed on stderr.
message_type
Always “error” string
error.message
Error message string
during
Always “restore” string
item
Usually, the path of the problematic
file
string
## Verbose Status
Verbose status provides details about the progress, including details about restored
files. Only printed if –verbose=2 is specified.
message_type
Always “verbose_status” string
action
Either “restored”, “updated”, “unchanged” or
## “deleted”
string
item
The item in question string

size
Size of the item in bytes uint64
## Summary
message_type
Always “summary” string
seconds_elapsed
Time since restore started uint64
total_files
Total number of files detected uint64
files_restored
Files restored uint64
files_skipped
Files skipped due to overwrite
setting
uint64
files_deleted
Files deleted uint64
total_bytes
Total number of bytes in restore set uint64
bytes_restored
Number of bytes restored uint64

bytes_skipped
Total size of skipped files uint64
snapshots
The snapshots command returns a single JSON array with objects of the structure
outlined below.
time
Timestamp of when the backup was started time.Time
parent
ID of the parent snapshot string
tree
ID of the root tree blob string
paths
List of paths included in the backup []string
hostname
Hostname of the backed up machine string
username
Username the backup command was run as string
uid
ID of owner uint32

gid
ID of group uint32
excludes
List of paths and globs excluded from the
backup
## []string
tags
List of tags for the snapshot in question []string
program_versi
on
restic version used to create snapshot string
summary
Snapshot statistics
SnapshotSummary
object
id
Snapshot ID string
short_id
Snapshot ID, short form (deprecated) string
SnapshotSummary object
The contained statistics reflect the information at the point64 in time when the snapshot
was created.

backup_start
Time at which the backup was started
time.Tim
e
backup_end
Time at which the backup was completed
time.Tim
e
files_new
Number of new files uint64
files_changed
Number of files that changed uint64
files_unmodified
Number of files that did not change uint64
dirs_new
Number of new directories uint64
dirs_changed
Number of directories that changed uint64
dirs_unmodified
Number of directories that did not change uint64
data_blobs
Number of data blobs added int64

tree_blobs
Number of tree blobs added int64
data_added
Amount of (uncompressed) data added, in bytes uint64
data_added_packed
Amount of data added (after compression), in
bytes
uint64
total_files_processe
d
Total number of files processed uint64
total_bytes_processe
d
Total number of bytes processed uint64
stats
The stats command returns a single JSON object.
total_size
Repository size in bytes
uint
## 64
total_file_count
Number of files backed up in the repository
uint
## 64

total_blob_count
Number of blobs in the repository
uint
## 64
snapshots_count
Number of processed snapshots
uint
## 64
total_uncompresse
d_size
Repository size in bytes if blobs were uncompressed
uint
## 64
compression_ratio
Factor by which the already compressed data has shrunk
due to compression
float
## 64
compression_progr
ess
Percentage of already compressed data
float
## 64
compression_space
## _saving
Overall space saving due to compression
float
## 64
tag
The tag command uses the JSON lines format with the following message types.
## Changed
message_type
Always “changed” string

old_snapshot_id
ID of the snapshot before the
change
string
new_snapshot_id
ID of the snapshot after the change string
## Summary
message_type
Always “summary” string
changed_snapshot_coun
t
Total number of changed
snapshots
int64
version
The version command returns a single JSON object.
message_type
Always “version” string
version
restic version string
go_version
Go compile
version
string

go_os
Go OS string
go_arch
Go architecture string
## Troubleshooting
The repository format used by restic is designed to be error resistant. In particular,
commands like, for example,
backup or prune can be interrupted at any point in time
without damaging the repository. You might have to run
unlock manually though, but
that’s it.
However, a repository might be damaged if some of its files are damaged or lost. This
can occur due to hardware failures, accidentally removing files from the repository or
bugs in the implementation of restic.
The following steps will help you recover a repository. This guide does not cover all
possible types of repository damages. Thus, if the steps do not work for you or you are
unsure how to proceed, then ask for help. Please always include the check output
discussed in the next section and what steps you’ve taken to repair the repository so far.
## ● Forum
● Our IRC channel #restic on irc.libera.chat
Make sure that you use the latest available restic version. It can contain bugfixes,
and improvements to simplify the repair of a repository. It might also contain a fix for
your repository problems!
- Find out what is damaged

The first step is always to check the repository.
restic check --read-data

using temporary cache in /tmp/restic-check-cache-1418935501
repository 12345678 opened (version 2, compression level auto)
created new cache in /tmp/restic-check-cache-1418935501
create exclusive lock for repository
load indexes
check all packs
check snapshots, trees and blobs
error for tree 7ef8ebab:
id 7ef8ebabc59aadda1a237d23ca7abac487b627a9b86508aa0194690446ff71f6 not found in
repository

7 / 7 snapshots
read all data
25 / 25 packs
Fatal: repository contains errors

## Note
This will download the whole repository. If retrieving data from the backend is
expensive, then omit the
--read-data option. Keep a copy of the check output as it might
be necessary later on!
If the output contains warnings that the ciphertext verification failed for some blobs in
the repository, then please ask for help in the forum or our IRC channel. These errors
are often caused by hardware problems which must be investigated and fixed.
Otherwise, the backup will be damaged again and again.
Similarly, if a repository is repeatedly damaged, please open an issue on GitHub as this
could indicate a bug somewhere. Please include the check output and additional
information that might help locate the problem.
If check detects damaged pack files, it will show instructions on how to repair them using
the
repair pack command. Use that command instead of the “Repair the index” section
in this guide.

- Backup the repository
Create a full copy of the repository if possible. Or at the very least make a copy of the
index and snapshots folders. This will allow you to roll back the repository if the repair
procedure fails. If your repository resides in a cloud storage, then you can for example
use rclone to make such a copy.
Please disable all regular operations on the repository to prevent unexpected changes.
## Especially,
forget or prune must be disabled as they could remove data unexpectedly.
## Warning
If you suspect hardware problems, then you must investigate those first. Otherwise, the
repository will soon be damaged again.
Please take the time to understand what the commands described in the following do. If
you are unsure, then ask for help in the forum or our IRC channel. Search whether your
issue is already known and solved. Please take a look at the forum and GitHub issues.
- Repair the index
## Note
If the check command tells you to run restic repair pack, then use that command
instead. It will repair the damaged pack files and also update the index.
Restic relies on its index to contain correct information about what data is stored in the
repository. Thus, the first step to repair a repository is to repair the index:
restic repair index

repository a14e5863 opened (version 2, compression level auto)
loading indexes...

getting pack files to read...
removing not found pack file
## 83ad44f59b05f6bce13376b022ac3194f24ca19e7a74926000b6e316ec6ea5a4

rebuilding index
27 / 27 packs processed
deleting obsolete index files
3 / 3 files deleted
done

This ensures that no longer existing files are removed from the index. All later steps to
repair the repository rely on a correct index. That is, you must always repair the index
first!
Please note that it is not recommended to repair the index unless the repository is
actually damaged.
- Run all backups (optional)
With a correct index, the backup command guarantees that newly created snapshots can
be restored successfully. It can also heal older snapshots, if the missing data is also
contained in the new snapshot.
Therefore, it is recommended to run all your backup tasks again. In some cases, this is
enough to fully repair the repository.
- Remove missing data from snapshots
If your repository is still missing data, then you can use the repair snapshots command
to remove all inaccessible data from the snapshots. That is, this will result in a limited
amount of data loss. Using the
--forget option, the command will automatically remove
the original, damaged snapshots.
restic repair snapshots --forget

snapshot 6979421e of [/home/user/restic/restic] at 2022-11-02 20:59:18.617503315 +0100
CET by user@host

file "/restic/internal/fuse/snapshots_dir.go": removed missing content

file "/restic/internal/restorer/restorer_unix_test.go": removed missing content
file "/restic/internal/walker/walker.go": removed missing content
saved new snapshot 7b094cea
removed old snapshot 6979421e

modified 1 snapshots

If you did not add the --forget option, then you have to manually delete all modified
snapshots using the
forget command. In the example above, you’d have to run restic
forget 6979421e
## .
- Check the repository again
Phew, we’re almost done now. To make sure that the repository has been successfully
repaired please run
check again.
restic check --read-data

using temporary cache in /tmp/restic-check-cache-2569290785
repository a14e5863 opened (version 2, compression level auto)
created new cache in /tmp/restic-check-cache-2569290785
create exclusive lock for repository
load indexes
check all packs
check snapshots, trees and blobs
7 / 7 snapshots
read all data
25 / 25 packs
no errors were found

If the check command did not complete with no errors were found, then the repository is
still damaged. At this point, please ask for help at the forum or our IRC channel #restic
on irc.libera.chat.
## Examples
Setting up restic with Amazon S3
## Preface

This tutorial will show you how to use restic with Amazon S3. It will show you how to
navigate the AWS web interface, create an S3 bucket, create a user with access to only
this bucket, and finally how to connect restic to this bucket.
## Prerequisites
You should already have a restic binary available on your system that you can run.
Furthermore, you should also have an account with AWS. You will likely need to provide
credit card details for billing purposes, even if you use their free-tier.
Logging into AWS
Point your browser to https://console.aws.amazon.com and log in using your AWS
account. You will be presented with the AWS homepage:

By using the “Services” button in the upper left corder, a menu of all services provided
by AWS can be opened:


For this tutorial, the Simple Storage Service (S3), as well as Identity and Access
Management (IAM) are relevant.
Creating the bucket
First, a bucket to store your backups in must be created. Using the “Services” menu,
navigate to S3. In case you already have some S3 buckets, you will see a list of them
here:


Click the “Create bucket” button and choose a name and region for your new bucket.
For the purpose of this tutorial, the bucket will be named
restic-demo and reside in
Frankfurt. Because the bucket name space is shared among all AWS users, the name
restic-demo may not be available to you. Be creative and choose a unique bucket name.


It is not necessary to configure any special properties or permissions of the bucket just
yet. Therefore, just finish the wizard without making any further changes:


The newly created restic-demo bucket will now appear on the list of S3 buckets:


Creating a user
Use the “Services” menu of the AWS web interface to navigate to IAM. This will bring
you to the IAM homepage. To create a new user, click on the “Users” menu entry on the
left:


In case you already have set-up users with IAM before, you will see a list of them here.
Use the “Add user” button at the top to create a new user:


For this tutorial, the new user will be named restic-demo-user. Feel free to choose your
own name that best fits your needs. This user will only ever access AWS through the
restic program and not through the web interface. Therefore, “Programmatic access” is
selected for “Access type”:


During the next step, permissions can be assigned to the new user. To use this user
with restic, it only needs access to the
restic-demo bucket. Select “Attach existing
policies directly”, which will bring up a list of pre-defined policies below. Afterwards, click
the “Create policy” button to create a custom policy:


A new browser window or tab will open with the policy wizard. In Amazon IAM, policies
are defined as JSON documents. For this tutorial, the “Visual editor” will be used to
generate a policy:


For restic to work, two permission statements must be created using the visual policy
editor. The first statement is set up as follows:
## Service: S3
Allow Actions: DeleteObject, GetObject, PutObject
Resources: arn:aws:s3:::restic-demo/*

This statement allows restic to create, read and delete objects inside the S3 bucket
named
restic-demo. Adjust the bucket’s name to the name of the bucket you created
earlier. Next, add a second statement using the “Add additional permissions” button:
## Service: S3
Allow Actions: ListBucket, GetBucketLocation
Resource: arn:aws:s3:::restic-demo

Again, substitute restic-demo with the actual name of your bucket. Note that, unlike
before, there is no
/* after the bucket name. This statement allows restic to list the
objects stored in the
restic-demo bucket and to query the bucket’s region.

Continue to the next step by clicking the “Review policy” button and enter a name and
description for this policy. For this tutorial, the policy will be named
restic-demo-policy.
Click “Create policy” to finish the process:

Go back to the browser window or tab where you were previously creating the new user.
Click the button labeled “Refresh” above the list of policies to make sure the newly
created policy is available to you. Afterwards, use the search function to search for the
restic-demo-policy. Select this policy using the checkbox on the left. Then, continue to
the next step.


The next page will present an overview of the user account that is about to be created.
If everything looks good, click “Create user” to complete the process:


After the user has been created, its access credentials will be displayed. They consist of
the “Access key ID” (think user name), and the “Secret access key” (think password).
Copy these down to a safe place.


You have now completed the configuration in AWS. Feel free to close your web browser
now.
Initializing the restic repository
Open a terminal and make sure you have the restic binary ready. First, choose a
password to encrypt your backups with. In this tutorial,
apg is used for this purpose:
apg -a 1 -m 32 -n 1 -M NCL
I9n7G7G0ZpDWA3GOcJbIuwQCGvGUBkU5

Note this password somewhere safe along with your AWS credentials. Next, the
configuration of restic will be placed into environment variables. This will include
sensitive information, such as your AWS secret and repository password. Therefore,
make sure the next commands do not end up in your shell’s history file. Adjust the
contents of the environment variables to fit your bucket’s name, region, and your user’s
API credentials.

unset HISTFILE
export AWS_DEFAULT_REGION="eu-west-1"
export RESTIC_REPOSITORY="s3:https://s3.amazonaws.com/restic-demo"
export AWS_ACCESS_KEY_ID="AKIAIOSFODNN7EXAMPLE"
export AWS_SECRET_ACCESS_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
export RESTIC_PASSWORD="I9n7G7G0ZpDWA3GOcJbIuwQCGvGUBkU5"

After the environment is set up, restic may be called to initialize the repository:
restic init
created restic backend b5c661a86a at s3:https://s3.amazonaws.com/restic-demo

Please note that knowledge of your password is required to access
the repository. Losing your password means that your data is
irrecoverably lost.

restic is now ready to be used with Amazon S3. Try to create a backup:
dd if=/dev/urandom bs=1M count=10 of=test.bin
10+0 records in
10+0 records out
10485760 bytes (10 MB, 10 MiB) copied, 0,0891322 s, 118 MB/s

restic backup test.bin
scan [/home/philip/restic-demo/test.bin]
scanned 0 directories, 1 files in 0:00
2.500 MiB/s  10.000 MiB / 10.000 MiB  1 / 1 items ... ETA 0:00
duration: 0:04, 2.47MiB/s
snapshot 10fdbace saved

restic snapshots
ID        Date                 Host        Tags        Directory
## ----------------------------------------------------------------------
10fdbace  2017-03-26 16:41:50  blackbox
## /home/philip/restic-demo/test.bin


A snapshot was created and stored in the S3 bucket. By default backups to Amazon S3
will use the
STANDARD storage class. Available storage classes include STANDARD,
STANDARD_IA, ONEZONE_IA, INTELLIGENT_TIERING, and REDUCED_REDUNDANCY. A different storage
class could have been specified in the above command by using
-o or --option:
restic backup -o s3.storage-class=REDUCED_REDUNDANCY test.bin


This snapshot may now be restored:
mkdir restore

restic restore 10fdbace --target restore
restoring <Snapshot 10fdbace of [/home/philip/restic-demo/test.bin] at 2017-03-26
16:41:50.201418102 +0200 CEST by philip@blackbox> to restore


ls restore/
test.bin

The snapshot was successfully restored. This concludes the tutorial.
Backing up your system without running restic as
root
## Motivation
Creating a complete backup of a machine requires a privileged process that is able to
read all files. On UNIX-like systems this is traditionally the
root user. Processes running
as root have superpower. They cannot only read all files but do also have the power to
modify the system in any possible way.
With great power comes great responsibility. If a process running as root malfunctions,
is exploited, or simply configured in a wrong way it can cause any possible damage to
the system. This means you only want to run programs as root that you trust completely.
And even if you trust a program, it is good and common practice to run it with the least
possible privileges.
Capabilities on Linux
Fortunately, Linux has functionality to divide root’s power into single separate
capabilities. You can remove these from a process running as root to restrict it. And you
can add capabilities to a process running as a normal user, which is what we are going
to do.

Full backup without root
To be able to completely backup a system, restic has to read all the files. Luckily Linux
knows a capability that allows precisely this. We can assign this single capability to
restic and then run it as an unprivileged user.
First we create a new user called restic that is going to create the backups:
useradd --system --create-home --shell /sbin/nologin restic

Then we download and install the restic binary into the user’s home directory (please
adjust the URL to refer to the latest restic version).
mkdir ~restic/bin
curl -L
https://github.com/restic/restic/releases/download/v0.12.1/restic_0.12.1_linux_amd64.b
z2
| bunzip2 > ~restic/bin/restic

Before we assign any special capability to the restic binary we restrict its permissions so
that only root and the newly created restic user can execute it. Otherwise another -
possibly untrusted - user could misuse the privileged restic binary to circumvent file
access controls.
chown root:restic ~restic/bin/restic
chmod 750 ~restic/bin/restic

Finally we can use setcap to add an extended attribute to the restic binary. On every
execution the system will read the extended attribute, interpret it and assign capabilities
accordingly.
setcap cap_dac_read_search=+ep ~restic/bin/restic

## Important

The capabilities of the setcap command only applies to this specific copy of the restic
binary. If you run
restic self-update or in any other way replace or update the binary,
the capabilities you added above will not be in effect for the new binary. To mitigate this,
simply run the
setcap command again, to make sure that the new binary has the same
and intended capabilities.
From now on the user restic can run restic to backup the whole system.
sudo -u restic /home/restic/bin/restic
--exclude={/dev,/media,/mnt,/proc,/run,/sys,/tmp,/var/tmp} -r /tmp backup /


## Participating
## Debug Logs
Set the environment variable DEBUG_LOG to let restic write extensive debug messages to
the specified filed, e.g.:
DEBUG_LOG=/tmp/restic-debug.log restic backup ~/work

If you suspect that there is a bug, you can have a look at the debug log. Please be
aware that the debug log might contain sensitive information such as file and directory
names.
The debug log will always contain all log messages restic generates. You can also
instruct restic to print some or all debug messages to stderr. These can also be limited
to e.g. a list of source files or a list of patterns for function names. The patterns are
globbing patterns (see the documentation for filepath.Match). Multiple patterns are
separated by commas. Patterns are case sensitive.

Printing all log messages to the console can be achieved by setting the file filter to *:
DEBUG_FILES=* restic check

If you want restic to just print all debug log messages from the files main.go and lock.go,
set the environment variable
DEBUG_FILES like this:
DEBUG_FILES=main.go,lock.go restic check

The following command line instructs restic to only print debug statements originating in
functions that match the pattern
*unlock* (case sensitive):
DEBUG_FUNCS=*unlock* restic check

## Debugging
The program can be built with debug support like this:
go run build.go -tags debug

This will make the restic debug <subcommand> available which can be used to inspect
internal data structures.
In addition, this enables profiling flags such as --cpu-profile and --mem-profile which
can help with investigation performance and memory usage issues. See
restic help for
more details and a few additional
--...-profile flags.
Running Restic with profiling enabled generates a .pprof file such as cpu.pprof. To view
a profile in a web browser, first make sure that the dot command from Graphviz is in the
PATH. Then, run go tool pprof -http : cpu.pprof.

## Contributing
Contributions are welcome! Please open an issue first (or add a comment to an
existing issue) if you plan to work on any code or add a new feature. This way, duplicate
work is prevented and we can discuss your ideas and design first.
More information and a description of the development environment can be found in
CONTRIBUTING.md. A document describing the design of restic and the data
structures stored on the back end is contained in Design.
If you’d like to start contributing to restic, but don’t know exactly what do to, have a look
at this great article by Dave Cheney: Suggestions for contributing to an Open Source
project. A few issues have been tagged with the label help wanted, you can start looking
at those.
## Security
Important: If you discover something that you believe to be a possible critical security
problem, please do not open a GitHub issue but send an email directly to
alexander@bumpern.de. If possible, please encrypt your email using the following PGP
key (0x91A6868BD3F7A907):
pub   4096R/91A6868BD3F7A907 2014-11-01
Key fingerprint = CF8F 18F2 8445 7597 3F79  D4E1 91A6 868B D3F7 A907
uid                          Alexander Neumann <alexander@bumpern.de>
sub   4096R/D5FC2ACF4043FDF1 2014-11-01

## Compatibility
Backward compatibility for backups is important so that our users are always able to
restore saved data. Therefore restic follows Semantic Versioning to clearly define which
versions are compatible. The repository and data structures contained therein are
considered the “Public API” in the sense of Semantic Versioning.

Once version 1.0.0 is released, we guarantee backward compatibility of all repositories
within one major version; as long as we do not increment the major version, data can be
read and restored. We strive to be fully backward compatible to all prior versions.
During initial development (versions prior to 1.0.0), maintainers and developers will do
their utmost to keep backwards compatibility and stability, although there might be
breaking changes without increasing the major version.
Building documentation
The restic documentation is built with Sphinx, therefore building it locally requires a
recent Python version and requirements listed in doc/requirements.txt. This example will
guide you through the process using virtualenv:
$ virtualenv venv # create virtual python environment
$ source venv/bin/activate # activate the virtual environment
$ cd doc
$ pip install -r requirements.txt # install dependencies
$ make html # build html documentation
$ # open _build/html/index.html with your favorite browser
## References
## Design
## Terminology
This section introduces terminology used in this document.
Repository: All data produced during a backup is sent to and stored in a repository in a
structured form, for example in a file system hierarchy with several subdirectories. A
repository implementation must be able to fulfill a number of operations, e.g. list the
contents.

Blob: A Blob combines a number of data bytes with identifying information like the
SHA-256 hash of the data and its length.
Pack: A Pack combines one or more Blobs, e.g. in a single file.
Snapshot: A Snapshot stands for the state of a file or directory that has been backed up
at some point in time. The state here means the content and meta data like the name
and modification time for the file or the directory and its contents.
Storage ID: A storage ID is the SHA-256 hash of the content stored in the repository.
This ID is required in order to load the file from the repository.
## Repository Format
All data is stored in a restic repository. A repository is able to store data of several
different types, which can later be requested based on an ID. This so-called “storage ID”
is the SHA-256 hash of the content of a file. All files in a repository are only written once
and never modified afterwards. Writing should occur atomically to prevent concurrent
operations from reading incomplete files. This allows accessing and even writing to the
repository with multiple clients in parallel. Only the prune operation removes data from
the repository.
Repositories consist of several directories and a top-level file called config. For all other
files stored in the repository, the name for the file is the lower case hexadecimal
representation of the storage ID, which is the SHA-256 hash of the file’s contents. This
allows for easy verification of files for accidental modifications, like disk read errors, by
simply running the program
sha256sum on the file and comparing its output to the file
name. If the prefix of a filename is unique amongst all the other files in the same
directory, the prefix may be used instead of the complete filename.
Apart from the files stored within the keys and data directories, all files are encrypted
with AES-256 in counter mode (CTR). The integrity of the encrypted data is secured by

a Poly1305-AES message authentication code (MAC). Files in the data directory (“pack
files”) consist of multiple parts which are all independently encrypted and authenticated,
see below.
In the first 16 bytes of each encrypted file the initialisation vector (IV) is stored. It is
followed by the encrypted data and completed by the 16 byte MAC. The format is:
## IV ||
## CIPHERTEXT || MAC
. The complete encryption overhead is 32 bytes. For each file, a new
random IV is selected.
The file config is encrypted this way and contains a JSON document like the following:
## {
## "version": 2,
## "id": "5956a3f67a6230d4a92cefb29529f10196c7d92582ec305fd71ff6d331d6271b",
## "chunker_polynomial": "25b468838dcb75"
## }

After decryption, restic first checks that the version field contains a version number that
it understands, otherwise it aborts. At the moment, the version is expected to be 1 or 2.
The list of changes in the repository format is contained in the section “Changes” below.
The field id holds a unique ID which consists of 32 random bytes, encoded in
hexadecimal. This uniquely identifies the repository, regardless if it is accessed via a
remote storage backend or locally. The field
chunker_polynomial contains a parameter
that is used for splitting large files into smaller chunks (see below).
## Repository Layout
The local and sftp backends are implemented using files and directories stored in a file
system. The directory layout is the same for both backend types and is also used for all
other remote backends.
The basic layout of a repository is shown here:

## /tmp/restic-repo
├── config
├── data
## │   ├── 21
## │   │   └── 2159dd48f8a24f33c307b750592773f8b71ff8d11452132a7b2e2a6a01611be1
## │   ├── 32
## │   │   └── 32ea976bc30771cebad8285cd99120ac8786f9ffd42141d452458089985043a5
## │   ├── 59
## │   │   └── 59fe4bcde59bd6222eba87795e35a90d82cd2f138a27b6835032b7b58173a426
## │   ├── 73
## │   │   └── 73d04e6125cf3c28a299cc2f3cca3b78ceac396e4fcf9575e34536b26782413c
## │   [...]
├── index
│   ├── c38f5fb68307c6a3e3aa945d556e325dc38f5fb68307c6a3e3aa945d556e325d
│   └── ca171b1b7394d90d330b265d90f506f9984043b342525f019788f97e745c71fd
├── keys
│   └── b02de829beeb3c01a63e6b25cbd421a98fef144f03b9a02e46eff9e2ca3f0bd7
├── locks
├── snapshots
## │   └── 22a5af1bdc6e616f8a29579458c49627e01b32210d09adb288d1ecda7c5711ec
└── tmp

A local repository can be initialized with the restic init command, e.g.:
restic -r /tmp/restic-repo init

## S3 Legacy Layout (deprecated)
Restic 0.17 is the last version that supports the legacy layout.
Unfortunately during development the Amazon S3 backend uses slightly different paths
(directory names use singular instead of plural for
key, lock, and snapshot files), and the
pack files are stored directly below the
data directory. The S3 Legacy repository layout
looks like this:
## /config
## /data
## ├── 2159dd48f8a24f33c307b750592773f8b71ff8d11452132a7b2e2a6a01611be1
## ├── 32ea976bc30771cebad8285cd99120ac8786f9ffd42141d452458089985043a5
## ├── 59fe4bcde59bd6222eba87795e35a90d82cd2f138a27b6835032b7b58173a426
## ├── 73d04e6125cf3c28a299cc2f3cca3b78ceac396e4fcf9575e34536b26782413c
## [...]
## /index
├── c38f5fb68307c6a3e3aa945d556e325dc38f5fb68307c6a3e3aa945d556e325d

└── ca171b1b7394d90d330b265d90f506f9984043b342525f019788f97e745c71fd
## /key
└── b02de829beeb3c01a63e6b25cbd421a98fef144f03b9a02e46eff9e2ca3f0bd7
## /lock
## /snapshot
## └── 22a5af1bdc6e616f8a29579458c49627e01b32210d09adb288d1ecda7c5711ec

## Pack Format
All files in the repository except Key and Pack files just contain raw data, stored as IV ||
Ciphertext || MAC
. Pack files may contain one or more Blobs of data.
A Pack’s structure is as follows:
EncryptedBlob1 || ... || EncryptedBlobN || EncryptedHeader || Header_Length

At the end of the Pack file is a header, which describes the content. The header is
encrypted and authenticated.
Header_Length is the length of the encrypted header
encoded as a four byte integer in little-endian encoding. Placing the header at the end
of a file allows writing the blobs in a continuous stream as soon as they are read during
the backup phase. This reduces code complexity and avoids having to re-write a file
once the pack is complete and the content and length of the header is known.
All the blobs (EncryptedBlob1, EncryptedBlobN etc.) are authenticated and encrypted
independently. This enables repository reorganisation without having to touch the
encrypted Blobs. In addition it also allows efficient indexing, for only the header needs
to be read in order to find out which Blobs are contained in the Pack. Since the header
is authenticated, authenticity of the header can be checked without having to read the
complete Pack.
After decryption, a Pack’s header consists of the following elements:
Type_Blob1 || Data_Blob1 ||
## [...]
Type_BlobN || Data_BlobN ||


The Blob type field is a single byte. What follows it depends on the type. The following
Blob types are defined:
## Typ
e
## Meaning Data
0b00 data blob
## Length(encrypted_blob) || Hash(plaintext_blob)
0b01 tree blob
## Length(encrypted_blob) || Hash(plaintext_blob)
## 0b10
compressed data
blob
## Length(encrypted_blob) || Length(plaintext_blob)
## || Hash(plaintext_blob)
0b11 compressed tree blob
## Length(encrypted_blob) || Length(plaintext_blob)
## || Hash(plaintext_blob)
This is enough to calculate the offsets for all the Blobs in the Pack. The length fields are
encoded as four byte integers in little-endian format. In the Data column,
Length(plaintext_blob) means the length of the decrypted and uncompressed data a
blob consists of.
All other types are invalid, more types may be added in the future. The compressed
types are only valid for repository format version 2. Data and tree blobs may be
compressed with the zstandard compression algorithm.

In repository format version 1, data and tree blobs should be stored in separate pack
files. In version 2, they must be stored in separate files. Compressed and non-compress
blobs of the same type may be mixed in a pack file.
For reconstructing the index or parsing a pack without an index, first the last four bytes
must be read in order to find the length of the header. Afterwards, the header can be
read and parsed, which yields all plaintext hashes, types, offsets and lengths of all
included blobs.
## Unpacked Data Format
Individual files for the index, locks or snapshots are encrypted and authenticated like
Data and Tree Blobs, so the outer structure is
IV || Ciphertext || MAC again. In
repository format version 1 the plaintext always consists of a JSON document which
must either be an object or an array. The JSON encoder must deterministically encode
the document and should match the behavior of the Go standard library implementation
in
encoding/json.
Repository format version 2 adds support for compression. The plaintext now starts with
a header to indicate the encoding version to distinguish it from plain JSON and to allow
for further evolution of the storage format:
encoding_version || data The encoding_version
field is encoded as one byte. For backwards compatibility the encoding versions ‘[’
(0x5b) and ‘{’ (0x7b) are used to mark that the whole plaintext (including the encoding
version byte) should treated as JSON document.
For new data the encoding version is currently always 2. For that version data contains a
JSON document compressed using the zstandard compression algorithm.
## Indexing
Index files contain information about Data and Tree Blobs and the Packs they are
contained in and store this information in the repository. When the local cached index is

not accessible any more, the index files can be downloaded and used to reconstruct the
index. The file encoding is described in the “Unpacked Data Format” section. The
plaintext consists of a JSON document like the following:
## {
## "supersedes": [
## "ed54ae36197f4745ebc4b54d10e0f623eaaaedd03013eb7ae90df881b7781452"
## ],
## "packs": [
## {
## "id": "73d04e6125cf3c28a299cc2f3cca3b78ceac396e4fcf9575e34536b26782413c",
## "blobs": [
## {
## "id": "3ec79977ef0cf5de7b08cd12b874cd0f62bbaf7f07f3497a5b1bbcc8cb39b1ce",
## "type": "data",
## "offset": 0,
## "length": 38,
// no 'uncompressed_length' as blob is not compressed
## },
## {
## "id": "9ccb846e60d90d4eb915848add7aa7ea1e4bbabfc60e573db9f7bfb2789afbae",
## "type": "data",
## "offset": 38,
## "length": 112,
## "uncompressed_length": 511,
## },
## {
## "id": "d3dc577b4ffd38cc4b32122cabf8655a0223ed22edfd93b353dc0c3f2b0fdf66",
## "type": "data",
## "offset": 150,
## "length": 123,
## "uncompressed_length": 234,
## }
## ]
## }, [...]
## ]
## }

This JSON document lists Packs and the blobs contained therein. In this example, the
## Pack
73d04e61 contains three data Blobs, the plaintext hashes are listed afterwards. The
length field corresponds to Length(encrypted_blob) in the pack file header. Field
uncompressed_length is only present for compressed blobs and therefore is never present
in version 1 of the repository format. It is set to the value of
## Length(blob).

The field supersedes lists the storage IDs of index files that have been replaced with the
current index file. This happens when index files are repacked, for example when old
snapshots are removed and Packs are recombined.
There may be an arbitrary number of index files, containing information on non-disjoint
sets of Packs. The number of packs described in a single file is chosen so that the file
size is kept below 8 MiB.
Keys, Encryption and MAC
All data stored by restic in the repository is encrypted with AES-256 in counter mode
and authenticated using Poly1305-AES. For encrypting new data first 16 bytes are read
from a cryptographically secure pseudo-random number generator as a random nonce.
This is used both as the IV for counter mode and the nonce for Poly1305. This
operation needs three keys: A 32 byte for AES-256 for encryption, a 16 byte AES key
and a 16 byte key for Poly1305. For details see the original paper The Poly1305-AES
message-authentication code by Dan Bernstein. The data is then encrypted with
AES-256 and afterwards a message authentication code (MAC) is computed over the
ciphertext, everything is then stored as IV || CIPHERTEXT || MAC.
The directory keys contains key files. These are simple JSON documents which contain
all data that is needed to derive the repository’s master encryption and message
authentication keys from a user’s password. The JSON document from the repository
can be pretty-printed for example by using the Python module
json (shortened to
increase readability):
$ python -mjson.tool /tmp/restic-repo/keys/b02de82*
## {
## "hostname": "kasimir",
## "username": "fd0"
## "kdf": "scrypt",
## "N": 65536,
## "r": 8,
## "p": 1,
"created": "2015-01-02T18:10:13.48307196+01:00",

## "data":
"tGwYeKoM0C4j4/9DFrVEmMGAldvEn/+iKC3te/QE/6ox/V4qz58FUOgMa0Bb1cIJ6asrypCx/Ti/pRXCPHLDk
IJbNYd2ybC+fLhFIJVLCvkMS+trdywsUkglUbTbi+7+Ldsul5jpAj9vTZ25ajDc+4FKtWEcCWL5ICAOoTAxnPg
T+Lh8ByGQBH6KbdWabqamLzTRWxePFoYuxa7yXgmj9A==",
## "salt":
"uW4fEI1+IOzj7ED9mVor+yTSJFd68DGlGOeLgJELYsTU5ikhG/83/+jGd4KKAaQdSrsfzrdOhAMftTSih5Ux6
w==",
## }

When the repository is opened by restic, the user is prompted for the repository
password. This is then used with
scrypt, a key derivation function (KDF), and the
supplied parameters (
N, r, p and salt) to derive 64 key bytes. The first 32 bytes are used
as the encryption key (for AES-256) and the last 32 bytes are used as the message
authentication key (for Poly1305-AES). These last 32 bytes are divided into a 16 byte
AES key
k followed by 16 bytes of secret key r. The key r is then masked for use with
Poly1305 (see the paper for details).
Those keys are used to authenticate and decrypt the bytes contained in the JSON field
data with AES-256 and Poly1305-AES as if they were any other blob (after removing the
Base64 encoding). If the password is incorrect or the key file has been tampered with,
the computed MAC will not match the last 16 bytes of the data, and restic exits with an
error. Otherwise, the data yields a JSON document which contains the master
encryption and message authentication keys for this repository (encoded in Base64).
The command
restic cat masterkey can be used as follows to decrypt and pretty-print
the master key:
restic -r /tmp/restic-repo cat masterkey
## {
## "mac": {
"k": "evFWd9wWlndL9jc501268g==",
"r": "E9eEDnSJZgqwTOkDtOp+Dw=="
## },
"encrypt": "UQCqa0lKZ94PygPxMRqkePTZnHRYh1k1pX2k2lM2v3Q=",
## }


All data in the repository is encrypted and authenticated with these master keys. For
encryption, the AES-256 algorithm in Counter mode is used. For message
authentication, Poly1305-AES is used as described above.
A repository can have several different passwords, with a key file for each. This way, the
password can be changed without having to re-encrypt all data.
## Snapshots
A snapshot represents a directory with all files and sub-directories at a given point in
time. For each backup that is made, a new snapshot is created. A snapshot is a JSON
document that is stored in a file below the directory
snapshots in the repository. It uses
the file encoding described in the “Unpacked Data Format” section. The filename is the
storage ID. This string is unique and used within restic to uniquely identify a snapshot.
The command restic cat snapshot can be used as follows to decrypt and pretty-print the
contents of a snapshot file:
restic -r /tmp/restic-repo cat snapshot 251c2e58
enter password for repository:
## {
"time": "2015-01-02T18:10:50.895208559+01:00",
## "tree": "2da81727b6585232894cfbb8f8bdab8d1eccd3d8f7c92bc934d62e62e618ffdf",
## "paths": [
## "/tmp/testdata"
## ],
## "hostname": "kasimir",
## "username": "fd0",
## "uid": 1000,
## "gid": 100,
## "tags": [
## "NL"
## ]
## }

Here it can be seen that this snapshot represents the contents of the directory
/tmp/testdata. The most important field is tree. When the meta data (e.g. the tags) of a
snapshot change, the snapshot needs to be re-encrypted and saved. This will change

the storage ID, so in order to relate these seemingly different snapshots, a field original
is introduced which contains the ID of the original snapshot, e.g. after adding the tag
## DE
to the snapshot above it becomes:
restic -r /tmp/restic-repo cat snapshot 22a5af1b
enter password for repository:
## {
"time": "2015-01-02T18:10:50.895208559+01:00",
## "tree": "2da81727b6585232894cfbb8f8bdab8d1eccd3d8f7c92bc934d62e62e618ffdf",
## "paths": [
## "/tmp/testdata"
## ],
## "hostname": "kasimir",
## "username": "fd0",
## "uid": 1000,
## "gid": 100,
## "tags": [
## "NL",
## "DE"
## ],
## "original": "251c2e5841355f743f9d4ffd3260bee765acee40a6229857e32b60446991b837"
## }

Once introduced, the original field is not modified when the snapshot’s meta data is
changed again.
All content within a restic repository is referenced according to its SHA-256 hash.
Before saving, each file is split into variable sized Blobs of data. The SHA-256 hashes
of all Blobs are saved in an ordered list which then represents the content of the file.
In order to relate these plaintext hashes to the actual location within a Pack file, an
index is used. If the index is not available, the header of all data Blobs can be read.
Trees and Data
A snapshot references a tree by the SHA-256 hash of the JSON string representation of
its contents. Trees and data are saved in pack files in a subdirectory of the directory
data.

The JSON encoder must deterministically encode the document and should match the
behavior of the Go standard library implementation in
encoding/json. This ensures that
trees can be properly deduplicated.
The command restic cat blob can be used to inspect the tree referenced above (piping
the output of the command to
jq . so that the JSON is indented):
restic -r /tmp/restic-repo cat blob
2da81727b6585232894cfbb8f8bdab8d1eccd3d8f7c92bc934d62e62e618ffdf | jq .
enter password for repository:
## {
## "nodes": [
## {
## "name": "testdata",
## "type": "dir",
## "mode": 493,
"mtime": "2014-12-22T14:47:59.912418701+01:00",
"atime": "2014-12-06T17:49:21.748468803+01:00",
"ctime": "2014-12-22T14:47:59.912418701+01:00",
## "uid": 1000,
## "gid": 100,
## "user": "fd0",
## "inode": 409704562,
"content": null,
## "subtree": "b26e315b0988ddcd1cee64c351d13a100fedbc9fdbb144a67d1b765ab280b4dc"
## }
## ]
## }

A tree contains a list of entries (in the field nodes) which contain meta data like a name
and timestamps. Note that there are some specialties of how this metadata is
generated:
● The name is quoted using strconv.Quote before being saved. This handles
non-unicode names, but also changes the representation of names containing
" or \.
● The filemode saved is the mode defined by fs.FileMode masked by
os.ModePerm | os.ModeType | os.ModeSetuid | os.ModeSetgid | os.ModeSticky
● When the entry references a directory, the field subtree contains the plain text
ID of another tree object.

● Check the implementation for a full struct definition.
When the command restic cat blob is used, the plaintext ID is needed to print a tree.
The tree referenced above can be dumped as follows:
restic -r /tmp/restic-repo cat blob
b26e315b0988ddcd1cee64c351d13a100fedbc9fdbb144a67d1b765ab280b4dc | jq .
enter password for repository:
## {
## "nodes": [
## {
## "name": "testfile",
## "type": "file",
## "mode": 420,
"mtime": "2014-12-06T17:50:23.34513538+01:00",
"atime": "2014-12-06T17:50:23.338468713+01:00",
"ctime": "2014-12-06T17:50:23.34513538+01:00",
## "uid": 1000,
## "gid": 100,
## "user": "fd0",
## "inode": 416863351,
## "size": 1234,
## "links": 1,
## "content": [
## "50f77b3b4291e8411a027b9f9b9e64658181cc676ce6ba9958b95f268cb1109d"
## ]
## },
## [...]
## ]
## }

This tree contains a file entry. This time, the subtree field is not present and the content
field contains a list with one plain text SHA-256 hash.
A symlink uses the following data structure:
restic -r /tmp/restic-repo cat blob
4c0a7d500bd1482ba01752e77c8d5a923304777d96b6522fae7c11e99b4e6fa6 | jq .
enter password for repository:
## {
## "nodes": [
## {
## "name": "testlink",
## "type": "symlink",
## "mode": 134218239,
"mtime": "2023-07-25T20:01:44.007465374+02:00",

"atime": "2023-07-25T20:01:44.007465374+02:00",
"ctime": "2023-07-25T20:01:44.007465374+02:00",
## "uid": 1000,
## "gid": 100,
## "user": "fd0",
## "inode": 33734827,
## "links": 1,
## "linktarget": "example_target",
"content": null
## },
## [...]
## ]
## }

The symlink target is stored in the field linktarget. As JSON strings can only contain
valid unicode, an exception applies if the linktarget is not a valid UTF-8 string. Since
restic 0.16.0, in such a case the linktarget_raw field contains a base64 encoded version
of the raw linktarget. The linktarget_raw field is only set if linktarget cannot be encoded
correctly.
The command restic cat blob can also be used to extract and decrypt data given a
plaintext ID, e.g. for the data mentioned above:
restic -r /tmp/restic-repo cat blob
50f77b3b4291e8411a027b9f9b9e64658181cc676ce6ba9958b95f268cb1109d | sha256sum
enter password for repository:
## 50f77b3b4291e8411a027b9f9b9e64658181cc676ce6ba9958b95f268cb1109d  -

As can be seen from the output of the program sha256sum, the hash matches the
plaintext hash from the map included in the tree above, so the correct data has been
returned.
## Locks
The restic repository structure is designed in a way that allows parallel access of
multiple instance of restic and even parallel writes. However, there are some functions
that work more efficient or even require exclusive access of the repository. In order to

implement these functions, restic processes are required to create a lock on the
repository before doing anything.
Locks come in two types: Exclusive and non-exclusive locks. At most one process can
have an exclusive lock on the repository, and during that time there must not be any
other locks (exclusive and non-exclusive). There may be multiple non-exclusive locks in
parallel.
A lock is a file in the subdir locks whose filename is the storage ID of the contents. It is
stored in the file encoding described in the “Unpacked Data Format” section and
contains the following JSON structure:
## {
"time": "2015-06-27T12:18:51.759239612+02:00",
"exclusive": false,
## "hostname": "kasimir",
## "username": "fd0",
## "pid": 13607,
## "uid": 1000,
## "gid": 100
## }

The field exclusive defines the type of lock. When a new lock is to be created, restic
checks all locks in the repository. When a lock is found, it is tested if the lock is stale,
which is the case for locks with timestamps older than 30 minutes. If the lock was
created on the same machine, even for younger locks it is tested whether the process is
still alive by sending a signal to it. If that fails, restic assumes that the process is dead
and considers the lock to be stale.
When a new lock is to be created and no other conflicting locks are detected, restic
creates a new lock, waits, and checks if other locks appeared in the repository.
Depending on the type of the other locks and the lock to be created, restic either
continues or fails. If the
--retry-lock option is specified, restic will retry creating the lock
periodically until it succeeds or the specified timeout expires.

Read and Write Ordering
The repository format allows writing (e.g. backup) and reading (e.g. restore) to happen
concurrently. As the data for each snapshot in a repository spans multiple files
(snapshot, index and packs), it is necessary to follow certain rules regarding the order in
which files are read and written. These ordering rules also guarantee that repository
modifications always maintain a correct repository even if the client or the storage
backend crashes for example due to a power cut or the (network) connection between
both is interrupted.
The correct order to access data in a repository is derived from the following set of
invariants that must be maintained at any time in a correct repository. Must in the
following is a strict requirement and will lead to data loss if not followed. Should will
require steps to fix a repository (e.g. rebuilding the index) if not followed, but should not
cause data loss. existing means that the referenced data is durably stored in the
repository.
● A snapshot must only reference an existing tree blob.
● A reachable tree blob must only reference tree and data blobs that exist
(recursively). Reachable means that the tree blob is reachable starting from a
snapshot.
● An index must only reference valid blobs in existing packs.
● All blobs referenced by a snapshot should be listed in an index.
This leads to the following recommended order to store data in a repository. First, pack
files, which contain data and tree blobs, must be written. Then the indexes which
reference blobs in these already written pack files. And finally the corresponding
snapshots.
Note that there is no need for a specific write order of data and tree blobs during a
backup as the blobs only become referenced once the corresponding snapshot is
uploaded.

Reading data should follow the opposite order compared to writing. Only once a
snapshot was written, it is guaranteed that all required data exists in the repository. This
especially means that the list of snapshots to read should be collected before loading
the repository index. The other way round can lead to a race condition where a recently
written snapshot is loaded but not its accompanying index, which results in a failure to
access the snapshot’s tree blob.
For removing or rewriting data from a repository the following rules must be followed,
which are derived from the above invariants.
● A client removing data must acquire an exclusive lock first to prevent conflicts
with other clients.
● A pack must be removed from the referencing index before it is deleted.
● Rewriting a pack must write the new pack, update the index (add an updated
index and delete the old one) and only then delete the old pack.
Backups and Deduplication
For creating a backup, restic scans the source directory for all files, sub-directories and
other entries. The data from each file is split into variable length Blobs cut at offsets
defined by a sliding window of 64 bytes. The implementation uses Rabin Fingerprints for
implementing this Content Defined Chunking (CDC). An irreducible polynomial is
selected at random and saved in the file
config when a repository is initialized, so that
watermark attacks are much harder.
Files smaller than 512 KiB are not split, Blobs are of 512 KiB to 8 MiB in size. The
implementation aims for 1 MiB Blob size on average.
For modified files, only modified Blobs have to be saved in a subsequent backup. This
even works if bytes are inserted or removed at arbitrary positions within the file.
## Threat Model

The design goals for restic include being able to securely store backups in a location
that is not completely trusted (e.g., a shared system where others can potentially
access the files) or even modify or delete them in the case of the system administrator.
General assumptions:
● The host system a backup is created on is trusted. This is the most basic
requirement, and it is essential for creating trustworthy backups.
● The user uses an authentic copy of restic.
● The user does not share the repository password with an attacker.
● The restic backup program is not designed to protect against attackers
deleting files at the storage location. There is nothing that can be done about
this. If this needs to be guaranteed, get a secure location without any access
from third parties.
● The whole repository is re-encrypted if a key is leaked. With the current key
management design, it is impossible to securely revoke a leaked key without
re-encrypting the whole repository.
● Advances in cryptography attacks against the cryptographic primitives used
by restic (i.e., AES-256-CTR-Poly1305-AES and SHA-256) have not
occurred. Such advances could render the confidentiality or integrity
protections provided by restic useless.
● Sufficient advances in computing have not occurred to make brute-force
attacks against restic’s cryptographic protections feasible.
The restic backup program guarantees the following:
● Unencrypted content of stored files and metadata cannot be accessed without
a password for the repository. Everything except the metadata included for
informational purposes in the key files is encrypted and authenticated. The
cache is also encrypted to prevent metadata leaks.
● Modifications to data stored in the repository (due to bad RAM, broken
harddisk, etc.) can be detected.

● Data that has been tampered will not be decrypted.
With the aforementioned assumptions and guarantees in mind, the following are
examples of things an adversary could achieve in various circumstances.
An adversary with read access to your backup storage location could:
● Attempt a brute force password guessing attack against a copy of the
repository (please use strong passwords with sufficient entropy).
● Infer which packs probably contain trees via file access patterns.
● Infer the size of backups by using creation timestamps of repository objects.
● As shown in the paper Chunking Attacks on File Backup Services using
Content-Defined Chunking by Boris Alexeev, Colin Percival and Yan X Zhang,
an attacker that can observe chunk sizes created for a known file can derive
the secret chunker polynomial. Knowledge of the polynomial might in some
cases allow an attacker to check whether certain large files are stored in a
repository. This has been mitigated in restic 0.18.0 by randomly assigning
chunks to pack files, which prevents an attacker from learning the chunk sizes
as the attacker can no longer determine to which file and which part of it a
chunk belongs. See #5295 for more details on the mitigation.
An adversary with network access could:
● Attempt to DoS the server storing the backup repository or the network
connection between client and server.
● Determine from where you create your backups (i.e., the location where the
requests originate).
● Determine where you store your backups (i.e., which provider/target system).
● Infer the size of backups by observing network traffic.
The following are examples of the implications associated with violating some of the
aforementioned assumptions.

An adversary who compromises (via malware, physical access, etc.) the host system
making backups could:
● Render the entire backup process untrustworthy (e.g., intercept password,
copy files, manipulate data).
● Create snapshots (containing garbage data) which cover all modified files and
wait until a trusted host has used
forget often enough to remove all correct
snapshots.
● Create a garbage snapshot for every existing snapshot with a slightly different
timestamp and wait until certain
forget configurations have been run, thereby
removing all correct snapshots at once.
An adversary with write access to your files at the storage location could:
● Delete or manipulate your backups, thereby impairing your ability to restore
files from the compromised storage location.
● Determine which files belong to what snapshot (e.g., based on the
timestamps of the stored files). When only these files are deleted, the
particular snapshot vanishes and all snapshots depending on data that has
been added in the snapshot cannot be restored completely. Restic is not
designed to detect this attack.
An adversary who compromises a host system with append-only (read+write allowed,
delete+overwrite denied) access to the backup repository could:
● Capture the password and decrypt backups from the past and in the future
(see the “leaked key” example below for related information).
● Render new backups untrustworthy after the host has been compromised
(due to having complete control over new backups). An attacker cannot
delete or manipulate old backups. As such, restoring old snapshots created
before a host compromise remains possible.

● Potentially manipulate the use of the forget command into deleting all
legitimate snapshots, keeping only bogus snapshots added by the attacker.
Ransomware might try this in order to leave only one option to get your data
back: paying the ransom. For safe use of
forget, please see the
corresponding documentation on removing backup snapshots and
append-only mode.
An adversary who has a leaked (decrypted) key for a repository could:
● Decrypt existing and future backup data. If multiple hosts backup into the
same repository, an attacker will get access to the backup data of every host.
Note that since the local encryption key gives access to the master key, a
password change will not prevent this. Changing the master key can currently
only be done using the copy command, which moves the data into a new
repository with a new master key, or by making a completely new repository
and new backup.
## Changes
## Repository Version 2
● Support compression for blobs (data/tree) and index / lock / snapshot files
## Local Cache
In order to speed up certain operations, restic manages a local cache of data. The
location of the cache directory depends on the operating system and the environment;
see Caching.
Each repository has its own cache sub-directory, consisting of the repository ID which is
chosen at
init. All cache directories for different repositories are independent of each
other.

Snapshots, Data and Indexes
Snapshot, Data and Index files are cached in the sub-directories snapshots, data and
index, as read from the repository.
## Expiry
Whenever a cache directory for a repository is used, that directory’s modification
timestamp is updated to the current time. By looking at the modification timestamps of
the repository cache directories it is easy to decide which directories are old and haven’t
been used in a long time. Those are probably stale and can be removed.
REST Backend
Restic can interact with HTTP Backend that respects the following REST API.
The following values are valid for {type}:
● data
● keys
● locks
● snapshots
● index
● config
The API version is selected via the Accept HTTP header in the request. The following
values are defined:
● application/vnd.x.restic.rest.v1 or empty: Select API version 1
● application/vnd.x.restic.rest.v2: Select API version 2

The server will respond with the value of the highest version it supports in the
Content-Type HTTP response header for the HTTP requests which should return JSON.
Any different value for this header means API version 1.
The placeholder {path} in this document is a path to the repository, so that multiple
different repositories can be accessed. The default path is /. The path must end with a
slash.
POST {path}?create=true
This request is used to initially create a new repository. The server responds with “200
OK” if the repository structure was created successfully or already exists, otherwise an
error is returned.
DELETE {path}
Deletes the repository on the server side. The server responds with “200 OK” if the
repository was successfully removed. If this function is not implemented the server
returns “501 Not Implemented”, if this it is denied by the server it returns “403
## Forbidden”.
HEAD {path}/config
Returns “200 OK” if the repository has a configuration, an HTTP error otherwise.
GET {path}/config
Returns the content of the configuration file if the repository has a configuration, an
HTTP error otherwise.
Response format: binary/octet-stream
POST {path}/config

Returns “200 OK” if the configuration of the request body has been saved, an HTTP
error otherwise.
GET {path}/{type}/
API version 1
Returns a JSON array containing the names of all the blobs stored for a given type,
example:
## [
## "245bc4c430d393f74fbe7b13325e30dbde9fb0745e50caad57c446c93d20096b",
## "85b420239efa1132c41cea0065452a40ebc20c6f8e0b132a5b2f5848360973ec",
## "8e2006bb5931a520f3c7009fe278d1ebb87eb72c3ff92a50c30e90f1b8cf3e60",
## "e75c8c407ea31ba399ab4109f28dd18c4c68303d8d86cc275432820c42ce3649"
## ]

API version 2
Returns a JSON array containing an object for each file of the given type. The objects
have two keys:
name for the file name, and size for the size in bytes.
## [
## {
## "name": "245bc4c430d393f74fbe7b13325e30dbde9fb0745e50caad57c446c93d20096b",
## "size": 2341058
## },
## {
## "name": "85b420239efa1132c41cea0065452a40ebc20c6f8e0b132a5b2f5848360973ec",
## "size": 2908900
## },
## {
## "name": "8e2006bb5931a520f3c7009fe278d1ebb87eb72c3ff92a50c30e90f1b8cf3e60",
## "size": 3030712
## },
## {
## "name": "e75c8c407ea31ba399ab4109f28dd18c4c68303d8d86cc275432820c42ce3649",
## "size": 2804
## }
## ]

HEAD {path}/{type}/{name}

Returns “200 OK” if the blob with the given name and type is stored in the repository,
“404 not found” otherwise. If the blob exists, the HTTP header
Content-Length is set to
the file size.
GET {path}/{type}/{name}
Returns the content of the blob with the given name and type if it is stored in the
repository, “404 not found” otherwise.
If the request specifies a partial read with a Range header field, then the status code of
the response is 206 instead of 200 and the response only contains the specified range.
Response format: binary/octet-stream
POST {path}/{type}/{name}
Saves the content of the request body as a blob with the given name and type, an
HTTP error otherwise.
Request format: binary/octet-stream
DELETE {path}/{type}/{name}
Returns “200 OK” if the blob with the given name and type has been deleted from the
repository, an HTTP error otherwise.
