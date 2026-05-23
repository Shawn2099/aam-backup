# rclone

# Show help for rclone commands, flags and backends.

## Synopsis

# Rclone syncs files to and from cloud storage providers as well as mounting them, listing them in lots of different ways.

# See the home page ([https://rclone.org/](https://rclone.org/)) for installation, usage, documentation, changelog and configuration walkthroughs.

# rclone \[flags\]

# 

## Options

#      \--alias-description string                            Description of the remote

#       \--alias-remote string                                 Remote or path to alias

#       \--archive-description string                          Description of the remote

#       \--archive-remote string                               Remote to wrap to read archives from

#       \--ask-password                                        Allow prompt for password for encrypted configuration (default true)

#       \--auto-confirm                                        If enabled, do not request console confirmation

#       \--azureblob-access-tier string                        Access tier of blob: hot, cool, cold or archive

#       \--azureblob-account string                            Azure Storage Account Name

#       \--azureblob-archive-tier-delete                       Delete archive tier blobs before overwriting

#       \--azureblob-chunk-size SizeSuffix                     Upload chunk size (default 4Mi)

#       \--azureblob-client-certificate-password string        Password for the certificate file (optional) (obscured)

#       \--azureblob-client-certificate-path string            Path to a PEM or PKCS12 certificate file including the private key

#       \--azureblob-client-id string                          The ID of the client in use

#       \--azureblob-client-secret string                      One of the service principal's client secrets

#       \--azureblob-client-send-certificate-chain             Send the certificate chain when using certificate auth

#       \--azureblob-connection-string string                  Storage Connection String

#       \--azureblob-copy-concurrency int                      Concurrency for multipart copy (default 512\)

#       \--azureblob-copy-cutoff SizeSuffix                    Cutoff for switching to multipart copy (default 8Mi)

#       \--azureblob-delete-snapshots string                   Set to specify how to deal with snapshots on blob deletion

#       \--azureblob-description string                        Description of the remote

#       \--azureblob-directory-markers                         Upload an empty object with a trailing slash when a new directory is created

#       \--azureblob-disable-checksum                          Don't store MD5 checksum with object metadata

#       \--azureblob-disable-instance-discovery                Skip requesting Microsoft Entra instance metadata

#       \--azureblob-encoding Encoding                         The encoding for the backend (default Slash,BackSlash,Del,Ctl,RightPeriod,InvalidUtf8)

#       \--azureblob-endpoint string                           Endpoint for the service

#       \--azureblob-env-auth                                  Read credentials from runtime (environment variables, CLI or MSI)

#       \--azureblob-key string                                Storage Account Shared Key

#       \--azureblob-list-chunk int                            Size of blob list (default 5000\)

#       \--azureblob-msi-client-id string                      Object ID of the user-assigned MSI to use, if any

#       \--azureblob-msi-mi-res-id string                      Azure resource ID of the user-assigned MSI to use, if any

#       \--azureblob-msi-object-id string                      Object ID of the user-assigned MSI to use, if any

#       \--azureblob-no-check-container                        If set, don't attempt to check the container exists or create it

#       \--azureblob-no-head-object                            If set, do not do HEAD before GET when getting objects

#       \--azureblob-password string                           The user's password (obscured)

#       \--azureblob-public-access string                      Public access level of a container: blob or container

#       \--azureblob-sas-url string                            SAS URL for container level access only

#       \--azureblob-service-principal-file string             Path to file containing credentials for use with a service principal

#       \--azureblob-tenant string                             ID of the service principal's tenant. Also called its directory ID

#       \--azureblob-upload-concurrency int                    Concurrency for multipart uploads (default 16\)

#       \--azureblob-upload-cutoff string                      Cutoff for switching to chunked upload (\<= 256 MiB) (deprecated)

#       \--azureblob-use-az                                    Use Azure CLI tool az for authentication

#       \--azureblob-use-copy-blob                             Whether to use the Copy Blob API when copying to the same storage account (default true)

#       \--azureblob-use-emulator                              Uses local storage emulator if provided as 'true'

#       \--azureblob-use-msi                                   Use a managed service identity to authenticate (only works in Azure)

#       \--azureblob-username string                           User name (usually an email address)

#       \--azurefiles-account string                           Azure Storage Account Name

#       \--azurefiles-chunk-size SizeSuffix                    Upload chunk size (default 4Mi)

#       \--azurefiles-client-certificate-password string       Password for the certificate file (optional) (obscured)

#       \--azurefiles-client-certificate-path string           Path to a PEM or PKCS12 certificate file including the private key

#       \--azurefiles-client-id string                         The ID of the client in use

#       \--azurefiles-client-secret string                     One of the service principal's client secrets

#       \--azurefiles-client-send-certificate-chain            Send the certificate chain when using certificate auth

#       \--azurefiles-connection-string string                 Storage Connection String

#       \--azurefiles-description string                       Description of the remote

#       \--azurefiles-disable-instance-discovery               Skip requesting Microsoft Entra instance metadata

#       \--azurefiles-encoding Encoding                        The encoding for the backend (default Slash,LtGt,DoubleQuote,Colon,Question,Asterisk,Pipe,BackSlash,Del,Ctl,RightPeriod,InvalidUtf8,Dot)

#       \--azurefiles-endpoint string                          Endpoint for the service

#       \--azurefiles-env-auth                                 Read credentials from runtime (environment variables, CLI or MSI)

#       \--azurefiles-key string                               Storage Account Shared Key

#       \--azurefiles-max-stream-size SizeSuffix               Max size for streamed files (default 10Gi)

#       \--azurefiles-msi-client-id string                     Object ID of the user-assigned MSI to use, if any

#       \--azurefiles-msi-mi-res-id string                     Azure resource ID of the user-assigned MSI to use, if any

#       \--azurefiles-msi-object-id string                     Object ID of the user-assigned MSI to use, if any

#       \--azurefiles-password string                          The user's password (obscured)

#       \--azurefiles-sas-url string                           SAS URL for container level access only

#       \--azurefiles-service-principal-file string            Path to file containing credentials for use with a service principal

#       \--azurefiles-share-name string                        Azure Files Share Name

#       \--azurefiles-tenant string                            ID of the service principal's tenant. Also called its directory ID

#       \--azurefiles-upload-concurrency int                   Concurrency for multipart uploads (default 16\)

#       \--azurefiles-use-az                                   Use Azure CLI tool az for authentication

#       \--azurefiles-use-emulator                             Uses local storage emulator if provided as 'true'

#       \--azurefiles-use-msi                                  Use a managed service identity to authenticate (only works in Azure)

#       \--azurefiles-username string                          User name (usually an email address)

#       \--b2-account string                                   Account ID or Application Key ID

#       \--b2-chunk-size SizeSuffix                            Upload chunk size (default 96Mi)

#       \--b2-copy-cutoff SizeSuffix                           Cutoff for switching to multipart copy (default 4Gi)

#       \--b2-description string                               Description of the remote

#       \--b2-disable-checksum                                 Disable checksums for large (\> upload cutoff) files

#       \--b2-download-auth-duration Duration                  Time before the public link authorization token will expire in s or suffix ms|s|m|h|d (default 1w)

#       \--b2-download-url string                              Custom endpoint for downloads

#       \--b2-encoding Encoding                                The encoding for the backend (default Slash,BackSlash,Del,Ctl,InvalidUtf8,Dot)

#       \--b2-endpoint string                                  Endpoint for the service

#       \--b2-hard-delete                                      Permanently delete files on remote removal, otherwise hide files

#       \--b2-key string                                       Application Key

#       \--b2-lifecycle int                                    Set the number of days deleted files should be kept when creating a bucket

#       \--b2-sse-customer-algorithm string                    If using SSE-C, the server-side encryption algorithm used when storing this object in B2

#       \--b2-sse-customer-key string                          To use SSE-C, you may provide the secret encryption key encoded in a UTF-8 compatible string to encrypt/decrypt your data

#       \--b2-sse-customer-key-base64 string                   To use SSE-C, you may provide the secret encryption key encoded in Base64 format to encrypt/decrypt your data

#       \--b2-sse-customer-key-md5 string                      If using SSE-C you may provide the secret encryption key MD5 checksum (optional)

#       \--b2-test-mode string                                 A flag string for X-Bz-Test-Mode header for debugging

#       \--b2-upload-concurrency int                           Concurrency for multipart uploads (default 4\)

#       \--b2-upload-cutoff SizeSuffix                         Cutoff for switching to chunked upload (default 200Mi)

#       \--b2-version-at Time                                  Show file versions as they were at the specified time (default off)

#       \--b2-versions                                         Include old versions in directory listings

#       \--backup-dir string                                   Make backups into hierarchy based in DIR

#       \--bind string                                         Local address to bind to for outgoing connections, IPv4, IPv6 or name

#       \--box-access-token string                             Box App Primary Access Token

#       \--box-auth-url string                                 Auth server URL

#       \--box-box-config-file string                          Box App config.json location

#       \--box-box-sub-type string                              (default "user")

#       \--box-client-credentials                              Use client credentials OAuth flow

#       \--box-client-id string                                OAuth Client Id

#       \--box-client-secret string                            OAuth Client Secret

#       \--box-commit-retries int                              Max number of times to try committing a multipart file (default 100\)

#       \--box-description string                              Description of the remote

#       \--box-encoding Encoding                               The encoding for the backend (default Slash,BackSlash,Del,Ctl,RightSpace,InvalidUtf8,Dot)

#       \--box-impersonate string                              Impersonate this user ID when using a service account

#       \--box-list-chunk int                                  Size of listing chunk 1-1000 (default 1000\)

#       \--box-owned-by string                                 Only show items owned by the login (email address) passed in

#       \--box-root-folder-id string                           Fill in for rclone to use a non root folder as its starting point

#       \--box-token string                                    OAuth Access Token as a JSON blob

#       \--box-token-url string                                Token server url

#       \--box-upload-cutoff SizeSuffix                        Cutoff for switching to multipart upload (\>= 50 MiB) (default 50Mi)

#       \--buffer-size SizeSuffix                              In memory buffer size when reading files for each \--transfer (default 16Mi)

#       \--bwlimit BwTimetable                                 Bandwidth limit in KiB/s, or use suffix B|K|M|G|T|P or a full timetable

#       \--bwlimit-file BwTimetable                            Bandwidth limit per file in KiB/s, or use suffix B|K|M|G|T|P or a full timetable

#       \--ca-cert stringArray                                 CA certificate used to verify servers

#       \--cache-chunk-clean-interval Duration                 How often should the cache perform cleanups of the chunk storage (default 1m0s)

#       \--cache-chunk-no-memory                               Disable the in-memory cache for storing chunks during streaming

#       \--cache-chunk-path string                             Directory to cache chunk files (default "$HOME/.cache/rclone/cache-backend")

#       \--cache-chunk-size SizeSuffix                         The size of a chunk (partial file data) (default 5Mi)

#       \--cache-chunk-total-size SizeSuffix                   The total size that the chunks can take up on the local disk (default 10Gi)

#       \--cache-db-path string                                Directory to store file structure metadata DB (default "$HOME/.cache/rclone/cache-backend")

#       \--cache-db-purge                                      Clear all the cached data for this remote on start

#       \--cache-db-wait-time Duration                         How long to wait for the DB to be available \- 0 is unlimited (default 1s)

#       \--cache-description string                            Description of the remote

#       \--cache-dir string                                    Directory rclone will use for caching (default "$HOME/.cache/rclone")

#       \--cache-info-age Duration                             How long to cache file structure information (directory listings, file size, times, etc.) (default 6h0m0s)

#       \--cache-plex-insecure string                          Skip all certificate verification when connecting to the Plex server

#       \--cache-plex-password string                          The password of the Plex user (obscured)

#       \--cache-plex-url string                               The URL of the Plex server

#       \--cache-plex-username string                          The username of the Plex user

#       \--cache-read-retries int                              How many times to retry a read from a cache storage (default 10\)

#       \--cache-remote string                                 Remote to cache

#       \--cache-rps int                                       Limits the number of requests per second to the source FS (-1 to disable) (default \-1)

#       \--cache-tmp-upload-path string                        Directory to keep temporary files until they are uploaded

#       \--cache-tmp-wait-time Duration                        How long should files be stored in local cache before being uploaded (default 15s)

#       \--cache-workers int                                   How many workers should run in parallel to download chunks (default 4\)

#       \--cache-writes                                        Cache file data on writes through the FS

#       \--check-first                                         Do all the checks before starting transfers

#       \--checkers int                                        Number of checkers to run in parallel (default 8\)

#   \-c, \--checksum                                            Check for changes with size & checksum (if available, or fallback to size only)

#       \--chunker-chunk-size SizeSuffix                       Files larger than chunk size will be split in chunks (default 2Gi)

#       \--chunker-description string                          Description of the remote

#       \--chunker-fail-hard                                   Choose how chunker should handle files with missing or invalid chunks

#       \--chunker-hash-type string                            Choose how chunker handles hash sums (default "md5")

#       \--chunker-remote string                               Remote to chunk/unchunk

#       \--client-cert string                                  Client SSL certificate (PEM) for mutual TLS auth

#       \--client-key string                                   Client SSL private key (PEM) for mutual TLS auth

#       \--client-pass string                                  Password for client SSL private key (PEM) for mutual TLS auth (obscured) (obscured)

#       \--cloudinary-adjust-media-files-extensions            Cloudinary handles media formats as a file attribute and strips it from the name, which is unlike most other file systems (default true)

#       \--cloudinary-api-key string                           Cloudinary API Key

#       \--cloudinary-api-secret string                        Cloudinary API Secret

#       \--cloudinary-cloud-name string                        Cloudinary Environment Name

#       \--cloudinary-description string                       Description of the remote

#       \--cloudinary-encoding Encoding                        The encoding for the backend (default Slash,LtGt,DoubleQuote,Question,Asterisk,Pipe,Hash,Percent,BackSlash,Del,Ctl,RightSpace,InvalidUtf8,Dot)

#       \--cloudinary-eventually-consistent-delay Duration     Wait N seconds for eventual consistency of the databases that support the backend operation (default 0s)

#       \--cloudinary-media-extensions stringArray             Cloudinary supported media extensions (default 3ds,3g2,3gp,ai,arw,avi,avif,bmp,bw,cr2,cr3,djvu,dng,eps3,fbx,flif,flv,gif,glb,gltf,hdp,heic,heif,ico,indd,jp2,jpe,jpeg,jpg,jxl,jxr,m2ts,mov,mp4,mpeg,mts,mxf,obj,ogv,pdf,ply,png,psd,svg,tga,tif,tiff,ts,u3ma,usdz,wdp,webm,webp,wmv)

#       \--cloudinary-upload-prefix string                     Specify the API endpoint for environments out of the US

#       \--cloudinary-upload-preset string                     Upload Preset to select asset manipulation on upload

#       \--color AUTO|NEVER|ALWAYS                             When to show colors (and other ANSI codes) AUTO|NEVER|ALWAYS (default AUTO)

#       \--combine-description string                          Description of the remote

#       \--combine-upstreams SpaceSepList                      Upstreams for combining

#       \--compare-dest stringArray                            Include additional server-side paths during comparison

#       \--compress-description string                         Description of the remote

#       \--compress-level string                               GZIP (levels \-2 to 9):

#       \--compress-mode string                                Compression mode (default "gzip")

#       \--compress-ram-cache-limit SizeSuffix                 Some remotes don't allow the upload of files with unknown size (default 20Mi)

#       \--compress-remote string                              Remote to compress

#       \--config string                                       Config file (default "$HOME/.config/rclone/rclone.conf")

#       \--contimeout Duration                                 Connect timeout (default 1m0s)

#       \--copy-dest stringArray                               Implies \--compare-dest but also copies files from paths into destination

#   \-L, \--copy-links                                          Follow symlinks and copy the pointed to item

#       \--cpuprofile string                                   Write cpu profile to file

#       \--crypt-description string                            Description of the remote

#       \--crypt-directory-name-encryption                     Option to either encrypt directory names or leave them intact (default true)

#       \--crypt-filename-encoding string                      How to encode the encrypted filename to text string (default "base32")

#       \--crypt-filename-encryption string                    How to encrypt the filenames (default "standard")

#       \--crypt-no-data-encryption                            Option to either encrypt file data or leave it unencrypted

#       \--crypt-pass-bad-blocks                               If set this will pass bad blocks through as all 0

#       \--crypt-password string                               Password or pass phrase for encryption (obscured)

#       \--crypt-password2 string                              Password or pass phrase for salt (obscured)

#       \--crypt-remote string                                 Remote to encrypt/decrypt

#       \--crypt-server-side-across-configs                    Deprecated: use \--server-side-across-configs instead

#       \--crypt-show-mapping                                  For all files listed show how the names encrypt

#       \--crypt-strict-names                                  If set, this will raise an error when crypt comes across a filename that can't be decrypted

#       \--crypt-suffix string                                 If this is set it will override the default suffix of ".bin" (default ".bin")

#       \--cutoff-mode HARD|SOFT|CAUTIOUS                      Mode to stop transfers when reaching the max transfer limit HARD|SOFT|CAUTIOUS (default HARD)

#       \--default-time Time                                   Time to show if modtime is unknown for files and directories (default 2000-01-01T00:00:00Z)

#       \--delete-after                                        When synchronizing, delete files on destination after transferring (default)

#       \--delete-before                                       When synchronizing, delete files on destination before transferring

#       \--delete-during                                       When synchronizing, delete files during transfer

#       \--delete-excluded                                     Delete files on dest excluded from sync

#       \--disable string                                      Disable a comma separated list of features (use \--disable help to see a list)

#       \--disable-http-keep-alives                            Disable HTTP keep-alives and use each connection once

#       \--disable-http2                                       Disable HTTP/2 in the global transport

#       \--doi-description string                              Description of the remote

#       \--doi-doi string                                      The DOI or the doi.org URL

#       \--doi-doi-resolver-api-url string                     The URL of the DOI resolver API to use

#       \--doi-provider string                                 DOI provider

#       \--drime-access-token string                           API Access token

#       \--drime-chunk-size SizeSuffix                         Chunk size to use for uploading (default 5Mi)

#       \--drime-description string                            Description of the remote

#       \--drime-encoding Encoding                             The encoding for the backend (default Slash,BackSlash,Del,Ctl,LeftSpace,RightSpace,InvalidUtf8,Dot)

#       \--drime-hard-delete                                   Delete files permanently rather than putting them into the trash

#       \--drime-list-chunk int                                Number of items to list in each call (default 1000\)

#       \--drime-root-folder-id string                         ID of the root folder

#       \--drime-upload-concurrency int                        Concurrency for multipart uploads and copies (default 4\)

#       \--drime-upload-cutoff SizeSuffix                      Cutoff for switching to chunked upload (default 200Mi)

#       \--drime-workspace-id string                           Account ID

#       \--drive-acknowledge-abuse                             Set to allow files which return cannotDownloadAbusiveFile to be downloaded

#       \--drive-allow-import-name-change                      Allow the filetype to change when uploading Google docs

#       \--drive-auth-owner-only                               Only consider files owned by the authenticated user

#       \--drive-auth-url string                               Auth server URL

#       \--drive-chunk-size SizeSuffix                         Upload chunk size (default 8Mi)

#       \--drive-client-credentials                            Use client credentials OAuth flow

#       \--drive-client-id string                              Google Application Client Id

#       \--drive-client-secret string                          OAuth Client Secret

#       \--drive-copy-shortcut-content                         Server side copy contents of shortcuts instead of the shortcut

#       \--drive-description string                            Description of the remote

#       \--drive-disable-http2                                 Disable drive using http2 (default true)

#       \--drive-encoding Encoding                             The encoding for the backend (default InvalidUtf8)

#       \--drive-env-auth                                      Get IAM credentials from runtime (environment variables or instance meta data if no env vars)

#       \--drive-export-formats string                         Comma separated list of preferred formats for downloading Google docs (default "docx,xlsx,pptx,svg")

#       \--drive-fast-list-bug-fix                             Work around a bug in Google Drive listing (default true)

#       \--drive-formats string                                Deprecated: See export\_formats

#       \--drive-impersonate string                            Impersonate this user when using a service account

#       \--drive-import-formats string                         Comma separated list of preferred formats for uploading Google docs

#       \--drive-keep-revision-forever                         Keep new head revision of each file forever

#       \--drive-list-chunk int                                Size of listing chunk 100-1000, 0 to disable (default 1000\)

#       \--drive-metadata-enforce-expansive-access             Whether the request should enforce expansive access rules

#       \--drive-metadata-labels Bits                          Control whether labels should be read or written in metadata (default off)

#       \--drive-metadata-owner Bits                           Control whether owner should be read or written in metadata (default read)

#       \--drive-metadata-permissions Bits                     Control whether permissions should be read or written in metadata (default off)

#       \--drive-pacer-burst int                               Number of API calls to allow without sleeping (default 100\)

#       \--drive-pacer-min-sleep Duration                      Minimum time to sleep between API calls (default 100ms)

#       \--drive-resource-key string                           Resource key for accessing a link-shared file

#       \--drive-root-folder-id string                         ID of the root folder

#       \--drive-scope string                                  Comma separated list of scopes that rclone should use when requesting access from drive

#       \--drive-server-side-across-configs                    Deprecated: use \--server-side-across-configs instead

#       \--drive-service-account-credentials string            Service Account Credentials JSON blob

#       \--drive-service-account-file string                   Service Account Credentials JSON file path

#       \--drive-shared-with-me                                Only show files that are shared with me

#       \--drive-show-all-gdocs                                Show all Google Docs including non-exportable ones in listings

#       \--drive-size-as-quota                                 Show sizes as storage quota usage, not actual size

#       \--drive-skip-checksum-gphotos                         Skip checksums on Google photos and videos only

#       \--drive-skip-dangling-shortcuts                       If set skip dangling shortcut files

#       \--drive-skip-gdocs                                    Skip google documents in all listings

#       \--drive-skip-shortcuts                                If set skip shortcut files

#       \--drive-starred-only                                  Only show files that are starred

#       \--drive-stop-on-download-limit                        Make download limit errors be fatal

#       \--drive-stop-on-upload-limit                          Make upload limit errors be fatal

#       \--drive-team-drive string                             ID of the Shared Drive (Team Drive)

#       \--drive-token string                                  OAuth Access Token as a JSON blob

#       \--drive-token-url string                              Token server url

#       \--drive-trashed-only                                  Only show files that are in the trash

#       \--drive-upload-cutoff SizeSuffix                      Cutoff for switching to chunked upload (default 8Mi)

#       \--drive-use-created-date                              Use file created date instead of modified date

#       \--drive-use-shared-date                               Use date file was shared instead of modified date

#       \--drive-use-trash                                     Send files to the trash instead of deleting permanently (default true)

#       \--drive-v2-download-min-size SizeSuffix               If Object's are greater, use drive v2 API to download (default off)

#       \--dropbox-auth-url string                             Auth server URL

#       \--dropbox-batch-mode string                           Upload file batching sync|async|off (default "sync")

#       \--dropbox-batch-size int                              Max number of files in upload batch

#       \--dropbox-batch-timeout Duration                      Max time to allow an idle upload batch before uploading (default 0s)

#       \--dropbox-chunk-size SizeSuffix                       Upload chunk size (\< 150Mi) (default 48Mi)

#       \--dropbox-client-credentials                          Use client credentials OAuth flow

#       \--dropbox-client-id string                            OAuth Client Id

#       \--dropbox-client-secret string                        OAuth Client Secret

#       \--dropbox-description string                          Description of the remote

#       \--dropbox-encoding Encoding                           The encoding for the backend (default Slash,BackSlash,Del,RightSpace,InvalidUtf8,Dot)

#       \--dropbox-export-formats CommaSepList                 Comma separated list of preferred formats for exporting files (default html,md)

#       \--dropbox-impersonate string                          Impersonate this user when using a business account

#       \--dropbox-pacer-min-sleep Duration                    Minimum time to sleep between API calls (default 10ms)

#       \--dropbox-root-namespace string                       Specify a different Dropbox namespace ID to use as the root for all paths

#       \--dropbox-shared-files                                Instructs rclone to work on individual shared files

#       \--dropbox-shared-folders                              Instructs rclone to work on shared folders

#       \--dropbox-show-all-exports                            Show all exportable files in listings

#       \--dropbox-skip-exports                                Skip exportable files in all listings

#       \--dropbox-token string                                OAuth Access Token as a JSON blob

#       \--dropbox-token-url string                            Token server url

#   \-n, \--dry-run                                             Do a trial run with no permanent changes

#       \--dscp string                                         Set DSCP value to connections, value or name, e.g. CS1, LE, DF, AF21

#       \--dump DumpFlags                                      List of items to dump from: headers, bodies, requests, responses, auth, filters, goroutines, openfiles, mapper

#       \--dump-bodies                                         Dump HTTP headers and bodies \- may contain sensitive info

#       \--dump-headers                                        Dump HTTP headers \- may contain sensitive info

#       \--error-on-no-transfer                                Sets exit code 9 if no files are transferred, useful in scripts

#       \--exclude stringArray                                 Exclude files matching pattern

#       \--exclude-from stringArray                            Read file exclude patterns from file (use \- to read from stdin)

#       \--exclude-if-present stringArray                      Exclude directories if filename is present

#       \--expect-continue-timeout Duration                    Timeout when using expect / 100-continue in HTTP (default 1s)

#       \--fast-list                                           Use recursive list if available; uses more memory but fewer transactions

#       \--fichier-api-key string                              Your API Key, get it from https://1fichier.com/console/params.pl

#       \--fichier-cdn                                         Set if you wish to use CDN download links

#       \--fichier-description string                          Description of the remote

#       \--fichier-encoding Encoding                           The encoding for the backend (default Slash,LtGt,DoubleQuote,SingleQuote,BackQuote,Dollar,BackSlash,Del,Ctl,LeftSpace,RightSpace,InvalidUtf8,Dot)

#       \--fichier-file-password string                        If you want to download a shared file that is password protected, add this parameter (obscured)

#       \--fichier-folder-password string                      If you want to list the files in a shared folder that is password protected, add this parameter (obscured)

#       \--fichier-shared-folder string                        If you want to download a shared folder, add this parameter

#       \--filefabric-description string                       Description of the remote

#       \--filefabric-encoding Encoding                        The encoding for the backend (default Slash,Del,Ctl,InvalidUtf8,Dot)

#       \--filefabric-permanent-token string                   Permanent Authentication Token

#       \--filefabric-root-folder-id string                    ID of the root folder

#       \--filefabric-token string                             Session Token

#       \--filefabric-token-expiry string                      Token expiry time

#       \--filefabric-url string                               URL of the Enterprise File Fabric to connect to

#       \--filefabric-version string                           Version read from the file fabric

#       \--filelu-chunk-size SizeSuffix                        Chunk size to use for uploading. Used for multipart uploads (default 64Mi)

#       \--filelu-description string                           Description of the remote

#       \--filelu-encoding Encoding                            The encoding for the backend (default Slash,LtGt,DoubleQuote,SingleQuote,BackQuote,Dollar,Colon,Question,Asterisk,Pipe,Hash,Percent,BackSlash,CrLf,Del,Ctl,LeftSpace,LeftPeriod,LeftTilde,LeftCrLfHtVt,RightSpace,RightPeriod,RightCrLfHtVt,InvalidUtf8,Dot,SquareBracket,Semicolon,Exclamation)

#       \--filelu-key string                                   Your FileLu Rclone key from My Account

#       \--filelu-upload-cutoff SizeSuffix                     Cutoff for switching to chunked upload. Any files larger than this will be uploaded in chunks of chunk\_size (default 500Mi)

#       \--filen-api-key string                                API Key for your Filen account (obscured)

#       \--filen-auth-version string                           Authentication Version (internal use only)

#       \--filen-base-folder-uuid string                       UUID of Account Root Directory (internal use only)

#       \--filen-description string                            Description of the remote

#       \--filen-email string                                  Email of your Filen account

#       \--filen-encoding Encoding                             The encoding for the backend (default Slash,Del,Ctl,InvalidUtf8,Dot)

#       \--filen-master-keys string                            Master Keys (internal use only)

#       \--filen-password string                               Password of your Filen account (obscured)

#       \--filen-private-key string                            Private RSA Key (internal use only)

#       \--filen-public-key string                             Public RSA Key (internal use only)

#       \--filen-upload-concurrency int                        Concurrency for chunked uploads (default 16\)

#       \--files-from stringArray                              Read list of source-file names from file (use \- to read from stdin)

#       \--files-from-raw stringArray                          Read list of source-file names from file without any processing of lines (use \- to read from stdin)

#       \--filescom-api-key string                             The API key used to authenticate with Files.com

#       \--filescom-description string                         Description of the remote

#       \--filescom-encoding Encoding                          The encoding for the backend (default Slash,BackSlash,Del,Ctl,RightSpace,RightCrLfHtVt,InvalidUtf8,Dot)

#       \--filescom-password string                            The password used to authenticate with Files.com (obscured)

#       \--filescom-site string                                Your site subdomain (e.g. mysite) or custom domain (e.g. myfiles.customdomain.com)

#       \--filescom-username string                            The username used to authenticate with Files.com

#   \-f, \--filter stringArray                                  Add a file filtering rule

#       \--filter-from stringArray                             Read file filtering patterns from a file (use \- to read from stdin)

#       \--fix-case                                            Force rename of case insensitive dest to match source

#       \--fs-cache-expire-duration Duration                   Cache remotes for this long (0 to disable caching) (default 5m0s)

#       \--fs-cache-expire-interval Duration                   Interval to check for expired remotes (default 1m0s)

#       \--ftp-allow-insecure-tls-ciphers                      Allow insecure TLS ciphers

#       \--ftp-ask-password                                    Allow asking for FTP password when needed

#       \--ftp-close-timeout Duration                          Maximum time to wait for a response to close (default 1m0s)

#       \--ftp-concurrency int                                 Maximum number of FTP simultaneous connections, 0 for unlimited

#       \--ftp-description string                              Description of the remote

#       \--ftp-disable-epsv                                    Disable using EPSV even if server advertises support

#       \--ftp-disable-mlsd                                    Disable using MLSD even if server advertises support

#       \--ftp-disable-tls13                                   Disable TLS 1.3 (workaround for FTP servers with buggy TLS)

#       \--ftp-disable-utf8                                    Disable using UTF-8 even if server advertises support

#       \--ftp-encoding Encoding                               The encoding for the backend (default Slash,Del,Ctl,RightSpace,Dot)

#       \--ftp-explicit-tls                                    Use Explicit FTPS (FTP over TLS)

#       \--ftp-force-list-hidden                               Use LIST \-a to force listing of hidden files and folders. This will disable the use of MLSD

#       \--ftp-host string                                     FTP host to connect to

#       \--ftp-http-proxy string                               URL for HTTP CONNECT proxy

#       \--ftp-idle-timeout Duration                           Max time before closing idle connections (default 1m0s)

#       \--ftp-no-check-certificate                            Do not verify the TLS certificate of the server

#       \--ftp-no-check-upload                                 Don't check the upload is OK

#       \--ftp-pass string                                     FTP password (obscured)

#       \--ftp-port int                                        FTP port number (default 21\)

#       \--ftp-shut-timeout Duration                           Maximum time to wait for data connection closing status (default 1m0s)

#       \--ftp-socks-proxy string                              Socks 5 proxy host

#       \--ftp-tls                                             Use Implicit FTPS (FTP over TLS)

#       \--ftp-tls-cache-size int                              Size of TLS session cache for all control and data connections (default 32\)

#       \--ftp-user string                                     FTP username (default "$USER")

#       \--ftp-writing-mdtm                                    Use MDTM to set modification time (VsFtpd quirk)

#       \--gcs-access-token string                             Short-lived access token

#       \--gcs-anonymous                                       Access public buckets and objects without credentials

#       \--gcs-auth-url string                                 Auth server URL

#       \--gcs-bucket-acl string                               Access Control List for new buckets

#       \--gcs-bucket-policy-only                              Access checks should use bucket-level IAM policies

#       \--gcs-client-credentials                              Use client credentials OAuth flow

#       \--gcs-client-id string                                OAuth Client Id

#       \--gcs-client-secret string                            OAuth Client Secret

#       \--gcs-decompress                                      If set this will decompress gzip encoded objects

#       \--gcs-description string                              Description of the remote

#       \--gcs-directory-markers                               Upload an empty object with a trailing slash when a new directory is created

#       \--gcs-encoding Encoding                               The encoding for the backend (default Slash,CrLf,InvalidUtf8,Dot)

#       \--gcs-endpoint string                                 Custom endpoint for the storage API. Leave blank to use the provider default

#       \--gcs-env-auth                                        Get GCP IAM credentials from runtime (environment variables or instance meta data if no env vars)

#       \--gcs-location string                                 Location for the newly created buckets

#       \--gcs-no-check-bucket                                 If set, don't attempt to check the bucket exists or create it

#       \--gcs-object-acl string                               Access Control List for new objects

#       \--gcs-project-number string                           Project number

#       \--gcs-service-account-file string                     Service Account Credentials JSON file path

#       \--gcs-storage-class string                            The storage class to use when storing objects in Google Cloud Storage

#       \--gcs-token string                                    OAuth Access Token as a JSON blob

#       \--gcs-token-url string                                Token server url

#       \--gcs-user-project string                             User project

#       \--gofile-access-token string                          API Access token

#       \--gofile-account-id string                            Account ID

#       \--gofile-description string                           Description of the remote

#       \--gofile-encoding Encoding                            The encoding for the backend (default Slash,LtGt,DoubleQuote,Colon,Question,Asterisk,Pipe,BackSlash,Del,Ctl,LeftPeriod,RightPeriod,InvalidUtf8,Dot,Exclamation)

#       \--gofile-list-chunk int                               Number of items to list in each call (default 1000\)

#       \--gofile-root-folder-id string                        ID of the root folder

#       \--gphotos-auth-url string                             Auth server URL

#       \--gphotos-batch-mode string                           Upload file batching sync|async|off (default "sync")

#       \--gphotos-batch-size int                              Max number of files in upload batch

#       \--gphotos-batch-timeout Duration                      Max time to allow an idle upload batch before uploading (default 0s)

#       \--gphotos-client-credentials                          Use client credentials OAuth flow

#       \--gphotos-client-id string                            OAuth Client Id

#       \--gphotos-client-secret string                        OAuth Client Secret

#       \--gphotos-description string                          Description of the remote

#       \--gphotos-encoding Encoding                           The encoding for the backend (default Slash,CrLf,InvalidUtf8,Dot)

#       \--gphotos-include-archived                            Also view and download archived media

#       \--gphotos-proxy string                                Use the gphotosdl proxy for downloading the full resolution images

#       \--gphotos-read-only                                   Set to make the Google Photos backend read only

#       \--gphotos-read-size                                   Set to read the size of media items

#       \--gphotos-start-year int                              Year limits the photos to be downloaded to those which are uploaded after the given year (default 2000\)

#       \--gphotos-token string                                OAuth Access Token as a JSON blob

#       \--gphotos-token-url string                            Token server url

#       \--hash-filter string                                  Partition filenames by hash k/n or randomly @/n

#       \--hasher-auto-size SizeSuffix                         Auto-update checksum for files smaller than this size (disabled by default)

#       \--hasher-description string                           Description of the remote

#       \--hasher-hashes CommaSepList                          Comma separated list of supported checksum types (default md5,sha1)

#       \--hasher-max-age Duration                             Maximum time to keep checksums in cache (0 \= no cache, off \= cache forever) (default off)

#       \--hasher-remote string                                Remote to cache checksums for (e.g. myRemote:path)

#       \--hdfs-data-transfer-protection string                Kerberos data transfer protection: authentication|integrity|privacy

#       \--hdfs-description string                             Description of the remote

#       \--hdfs-encoding Encoding                              The encoding for the backend (default Slash,Colon,Del,Ctl,InvalidUtf8,Dot)

#       \--hdfs-namenode CommaSepList                          Hadoop name nodes and ports

#       \--hdfs-service-principal-name string                  Kerberos service principal name for the namenode

#       \--hdfs-username string                                Hadoop user name

#       \--header stringArray                                  Set HTTP header for all transactions

#       \--header-download stringArray                         Set HTTP header for download transactions

#       \--header-upload stringArray                           Set HTTP header for upload transactions

#   \-h, \--help                                                help for rclone

#       \--hidrive-auth-url string                             Auth server URL

#       \--hidrive-chunk-size SizeSuffix                       Chunksize for chunked uploads (default 48Mi)

#       \--hidrive-client-credentials                          Use client credentials OAuth flow

#       \--hidrive-client-id string                            OAuth Client Id

#       \--hidrive-client-secret string                        OAuth Client Secret

#       \--hidrive-description string                          Description of the remote

#       \--hidrive-disable-fetching-member-count               Do not fetch number of objects in directories unless it is absolutely necessary

#       \--hidrive-encoding Encoding                           The encoding for the backend (default Slash,Dot)

#       \--hidrive-endpoint string                             Endpoint for the service (default "https://api.hidrive.strato.com/2.1")

#       \--hidrive-root-prefix string                          The root/parent folder for all paths (default "/")

#       \--hidrive-scope-access string                         Access permissions that rclone should use when requesting access from HiDrive (default "rw")

#       \--hidrive-scope-role string                           User-level that rclone should use when requesting access from HiDrive (default "user")

#       \--hidrive-token string                                OAuth Access Token as a JSON blob

#       \--hidrive-token-url string                            Token server url

#       \--hidrive-upload-concurrency int                      Concurrency for chunked uploads (default 4\)

#       \--hidrive-upload-cutoff SizeSuffix                    Cutoff/Threshold for chunked uploads (default 96Mi)

#       \--http-description string                             Description of the remote

#       \--http-headers CommaSepList                           Set HTTP headers for all transactions

#       \--http-no-escape                                      Do not escape URL metacharacters in path names

#       \--http-no-head                                        Don't use HEAD requests

#       \--http-no-slash                                       Set this if the site doesn't end directories with /

#       \--http-proxy string                                   HTTP proxy URL

#       \--http-url string                                     URL of HTTP host to connect to

#       \--human-readable                                      Print numbers in a human-readable format, sizes with suffix Ki|Mi|Gi|Ti|Pi

#       \--iclouddrive-apple-id string                         Apple ID

#       \--iclouddrive-client-id string                        Client id (default "d39ba9916b7251055b22c7f910e2ea796ee65e98b2ddecea8f5dde8d9d1a815d")

#       \--iclouddrive-description string                      Description of the remote

#       \--iclouddrive-encoding Encoding                       The encoding for the backend (default Slash,BackSlash,Del,Ctl,InvalidUtf8,Dot)

#       \--iclouddrive-password string                         Password (obscured)

#       \--ignore-case                                         Ignore case in filters (case insensitive)

#       \--ignore-case-sync                                    Ignore case when synchronizing

#       \--ignore-checksum                                     Skip post copy check of checksums

#       \--ignore-errors                                       Delete even if there are I/O errors

#       \--ignore-existing                                     Skip all files that exist on destination

#       \--ignore-size                                         Ignore size when skipping use modtime or checksum

#   \-I, \--ignore-times                                        Don't skip items that match size and time \- transfer all unconditionally

#       \--imagekit-description string                         Description of the remote

#       \--imagekit-encoding Encoding                          The encoding for the backend (default Slash,LtGt,DoubleQuote,Dollar,Question,Hash,Percent,BackSlash,Del,Ctl,InvalidUtf8,Dot,SquareBracket)

#       \--imagekit-endpoint string                            You can find your ImageKit.io URL endpoint in your \[dashboard\](https://imagekit.io/dashboard/developer/api-keys)

#       \--imagekit-only-signed Restrict unsigned image URLs   If you have configured Restrict unsigned image URLs in your dashboard settings, set this to true

#       \--imagekit-private-key string                         You can find your ImageKit.io private key in your \[dashboard\](https://imagekit.io/dashboard/developer/api-keys)

#       \--imagekit-public-key string                          You can find your ImageKit.io public key in your \[dashboard\](https://imagekit.io/dashboard/developer/api-keys)

#       \--imagekit-upload-tags string                         Tags to add to the uploaded files, e.g. "tag1,tag2"

#       \--imagekit-versions                                   Include old versions in directory listings

#       \--immutable                                           Do not modify files, fail if existing files have been modified

#       \--include stringArray                                 Include files matching pattern

#       \--include-from stringArray                            Read file include patterns from file (use \- to read from stdin)

#       \--inplace                                             Download directly to destination file instead of atomic download to temp/rename

#   \-i, \--interactive                                         Enable interactive mode

#       \--internetarchive-access-key-id string                IAS3 Access Key

#       \--internetarchive-description string                  Description of the remote

#       \--internetarchive-disable-checksum                    Don't ask the server to test against MD5 checksum calculated by rclone (default true)

#       \--internetarchive-encoding Encoding                   The encoding for the backend (default Slash,LtGt,CrLf,Del,Ctl,InvalidUtf8,Dot)

#       \--internetarchive-endpoint string                     IAS3 Endpoint (default "https://s3.us.archive.org")

#       \--internetarchive-front-endpoint string               Host of InternetArchive Frontend (default "https://archive.org")

#       \--internetarchive-item-derive                         Whether to trigger derive on the IA item or not. If set to false, the item will not be derived by IA upon upload (default true)

#       \--internetarchive-item-metadata stringArray           Metadata to be set on the IA item, this is different from file-level metadata that can be set using \--metadata-set

#       \--internetarchive-secret-access-key string            IAS3 Secret Key (password)

#       \--internetarchive-wait-archive Duration               Timeout for waiting the server's processing tasks (specifically archive and book\_op) to finish (default 0s)

#       \--internxt-description string                         Description of the remote

#       \--internxt-email string                               Email of your Internxt account

#       \--internxt-encoding Encoding                          The encoding for the backend (default Slash,BackSlash,CrLf,RightPeriod,InvalidUtf8,Dot)

#       \--internxt-pass string                                Password (obscured)

#       \--internxt-skip-hash-validation                       Skip hash validation when downloading files (default true)

#       \--jottacloud-auth-url string                          Auth server URL

#       \--jottacloud-client-credentials                       Use client credentials OAuth flow

#       \--jottacloud-client-id string                         OAuth Client Id

#       \--jottacloud-client-secret string                     OAuth Client Secret

#       \--jottacloud-description string                       Description of the remote

#       \--jottacloud-encoding Encoding                        The encoding for the backend (default Slash,LtGt,DoubleQuote,Colon,Question,Asterisk,Pipe,Del,Ctl,InvalidUtf8,Dot)

#       \--jottacloud-hard-delete                              Delete files permanently rather than putting them into the trash

#       \--jottacloud-md5-memory-limit SizeSuffix              Files bigger than this will be cached on disk to calculate the MD5 if required (default 10Mi)

#       \--jottacloud-no-versions                              Avoid server side versioning by deleting files and recreating files instead of overwriting them

#       \--jottacloud-token string                             OAuth Access Token as a JSON blob

#       \--jottacloud-token-url string                         Token server url

#       \--jottacloud-trashed-only                             Only show files that are in the trash

#       \--jottacloud-upload-resume-limit SizeSuffix           Files bigger than this can be resumed if the upload fail's (default 10Mi)

#       \--koofr-description string                            Description of the remote

#       \--koofr-encoding Encoding                             The encoding for the backend (default Slash,BackSlash,Del,Ctl,InvalidUtf8,Dot)

#       \--koofr-endpoint string                               The Koofr API endpoint to use

#       \--koofr-mountid string                                Mount ID of the mount to use

#       \--koofr-password string                               Your password for rclone generate one at https://app.koofr.net/app/admin/preferences/password (obscured)

#       \--koofr-provider string                               Choose your storage provider

#       \--koofr-setmtime                                      Does the backend support setting modification time (default true)

#       \--koofr-user string                                   Your user name

#       \--kv-lock-time Duration                               Maximum time to keep key-value database locked by process (default 1s)

#       \--linkbox-description string                          Description of the remote

#       \--linkbox-token string                                Token from https://www.linkbox.to/admin/account

#   \-l, \--links                                               Translate symlinks to/from regular files with a '.rclonelink' extension

#       \--list-cutoff int                                     To save memory, sort directory listings on disk above this threshold (default 1000000\)

#       \--local-case-insensitive                              Force the filesystem to report itself as case insensitive

#       \--local-case-sensitive                                Force the filesystem to report itself as case sensitive

#       \--local-description string                            Description of the remote

#       \--local-encoding Encoding                             The encoding for the backend (default Slash,Dot)

#       \--local-hashes CommaSepList                           Comma separated list of supported checksum types

#       \--local-links                                         Translate symlinks to/from regular files with a '.rclonelink' extension for the local backend

#       \--local-no-check-updated                              Don't check to see if the files change during upload

#       \--local-no-clone                                      Disable reflink cloning for server-side copies

#       \--local-no-preallocate                                Disable preallocation of disk space for transferred files

#       \--local-no-set-modtime                                Disable setting modtime

#       \--local-no-sparse                                     Disable sparse files for multi-thread downloads

#       \--local-nounc                                         Disable UNC (long path names) conversion on Windows

#       \--local-time-type mtime|atime|btime|ctime             Set what kind of time is returned (default mtime)

#       \--local-unicode-normalization                         Apply unicode NFC normalization to paths and filenames

#       \--local-zero-size-links                               Assume the Stat size of links is zero (and read them instead) (deprecated)

#       \--log-file string                                     Log everything to this file

#       \--log-file-compress                                   If set, compress rotated log files using gzip

#       \--log-file-max-age Duration                           Maximum duration to retain old log files (eg "7d") (default 0s)

#       \--log-file-max-backups int                            Maximum number of old log files to retain

#       \--log-file-max-size SizeSuffix                        Maximum size of the log file before it's rotated (eg "10M") (default off)

#       \--log-format Bits                                     Comma separated list of log format options (default date,time)

#       \--log-level LogLevel                                  Log level DEBUG|INFO|NOTICE|ERROR (default NOTICE)

#       \--log-systemd                                         Activate systemd integration for the logger

#       \--low-level-retries int                               Number of low level retries to do (default 10\)

#       \--mailru-auth-url string                              Auth server URL

#       \--mailru-check-hash                                   What should copy do if file checksum is mismatched or invalid (default true)

#       \--mailru-client-credentials                           Use client credentials OAuth flow

#       \--mailru-client-id string                             OAuth Client Id

#       \--mailru-client-secret string                         OAuth Client Secret

#       \--mailru-description string                           Description of the remote

#       \--mailru-encoding Encoding                            The encoding for the backend (default Slash,LtGt,DoubleQuote,Colon,Question,Asterisk,Pipe,BackSlash,Del,Ctl,InvalidUtf8,Dot)

#       \--mailru-pass string                                  Password (obscured)

#       \--mailru-speedup-enable                               Skip full upload if there is another file with same data hash (default true)

#       \--mailru-speedup-file-patterns string                 Comma separated list of file name patterns eligible for speedup (put by hash) (default "\*.mkv,\*.avi,\*.mp4,\*.mp3,\*.zip,\*.gz,\*.rar,\*.pdf")

#       \--mailru-speedup-max-disk SizeSuffix                  This option allows you to disable speedup (put by hash) for large files (default 3Gi)

#       \--mailru-speedup-max-memory SizeSuffix                Files larger than the size given below will always be hashed on disk (default 32Mi)

#       \--mailru-token string                                 OAuth Access Token as a JSON blob

#       \--mailru-token-url string                             Token server url

#       \--mailru-user string                                  User name (usually email)

#       \--max-age Duration                                    Only transfer files younger than this in s or suffix ms|s|m|h|d|w|M|y (default off)

#       \--max-backlog int                                     Maximum number of objects in sync or check backlog (default 10000\)

#       \--max-buffer-memory SizeSuffix                        If set, don't allocate more than this amount of memory as buffers (default off)

#       \--max-connections int                                 Maximum number of simultaneous backend API connections, 0 for unlimited

#       \--max-delete int                                      When synchronizing, limit the number of deletes (default \-1)

#       \--max-delete-size SizeSuffix                          When synchronizing, limit the total size of deletes (default off)

#       \--max-depth int                                       If set limits the recursion depth to this (default \-1)

#       \--max-duration Duration                               Maximum duration rclone will transfer data for (default 0s)

#       \--max-size SizeSuffix                                 Only transfer files smaller than this in KiB or suffix B|K|M|G|T|P (default off)

#       \--max-stats-groups int                                Maximum number of stats groups to keep in memory, on max oldest is discarded (default 1000\)

#       \--max-transfer SizeSuffix                             Maximum size of data to transfer (default off)

#       \--mega-2fa string                                     The 2FA code of your MEGA account if the account is set up with one

#       \--mega-debug                                          Output more debug from Mega

#       \--mega-description string                             Description of the remote

#       \--mega-encoding Encoding                              The encoding for the backend (default Slash,InvalidUtf8,Dot)

#       \--mega-hard-delete                                    Delete files permanently rather than putting them into the trash

#       \--mega-pass string                                    Password (obscured)

#       \--mega-use-https                                      Use HTTPS for transfers

#       \--mega-user string                                    User name

#       \--memory-description string                           Description of the remote

#       \--memory-discard                                      If set all writes will be discarded and reads will return an error

#       \--memprofile string                                   Write memory profile to file

#   \-M, \--metadata                                            If set, preserve metadata when copying objects

#       \--metadata-exclude stringArray                        Exclude metadatas matching pattern

#       \--metadata-exclude-from stringArray                   Read metadata exclude patterns from file (use \- to read from stdin)

#       \--metadata-filter stringArray                         Add a metadata filtering rule

#       \--metadata-filter-from stringArray                    Read metadata filtering patterns from a file (use \- to read from stdin)

#       \--metadata-include stringArray                        Include metadatas matching pattern

#       \--metadata-include-from stringArray                   Read metadata include patterns from file (use \- to read from stdin)

#       \--metadata-mapper SpaceSepList                        Program to run to transforming metadata before upload

#       \--metadata-set stringArray                            Add metadata key=value when uploading

#       \--metrics-addr stringArray                            IPaddress:Port or :Port to bind metrics server to

#       \--metrics-allow-origin string                         Origin which cross-domain request (CORS) can be executed from

#       \--metrics-baseurl string                              Prefix for URLs \- leave blank for root

#       \--metrics-cert string                                 TLS PEM key (concatenation of certificate and CA certificate)

#       \--metrics-client-ca string                           Client certificate authority to verify clients with

#       \--metrics-htpasswd string                             A htpasswd file \- if not provided no authentication is done

#       \--metrics-key string                                  TLS PEM Private key

#       \--metrics-max-header-bytes int                        Maximum size of request header (default 4096\)

#       \--metrics-min-tls-version string                      Minimum TLS version that is acceptable (default "tls1.0")

#       \--metrics-pass string                                 Password for authentication

#       \--metrics-realm string                                Realm for authentication

#       \--metrics-salt string                                 Password hashing salt (default "dlPL2MqE")

#       \--metrics-server-read-timeout Duration                Timeout for server reading data (default 1h0m0s)

#       \--metrics-server-write-timeout Duration               Timeout for server writing data (default 1h0m0s)

#       \--metrics-template string                             User-specified template

#       \--metrics-user string                                 User name for authentication

#       \--metrics-user-from-header string                     User name from a defined HTTP header

#       \--min-age Duration                                    Only transfer files older than this in s or suffix ms|s|m|h|d|w|M|y (default off)

#       \--min-size SizeSuffix                                 Only transfer files bigger than this in KiB or suffix B|K|M|G|T|P (default off)

#       \--modify-window Duration                              Max time diff to be considered the same (default 1ns)

#       \--multi-thread-chunk-size SizeSuffix                  Chunk size for multi-thread downloads / uploads, if not set by filesystem (default 64Mi)

#       \--multi-thread-cutoff SizeSuffix                      Use multi-thread downloads for files above this size (default 256Mi)

#       \--multi-thread-streams int                            Number of streams to use for multi-thread downloads (default 4\)

#       \--multi-thread-write-buffer-size SizeSuffix           In memory buffer size for writing when in multi-thread mode (default 128Ki)

#       \--name-transform stringArray                          Transform paths during the copy process

#       \--netstorage-account string                           Set the NetStorage account name

#       \--netstorage-description string                       Description of the remote

#       \--netstorage-host string                              Domain+path of NetStorage host to connect to

#       \--netstorage-protocol string                          Select between HTTP or HTTPS protocol (default "https")

#       \--netstorage-secret string                            Set the NetStorage account secret/G2O key for authentication (obscured)

#       \--no-check-certificate                                Do not verify the server SSL certificate (insecure)

#       \--no-check-dest                                       Don't check the destination, copy regardless

#       \--no-console                                          Hide console window (supported on Windows only)

#       \--no-gzip-encoding                                    Don't set Accept-Encoding: gzip

#       \--no-traverse                                         Don't traverse destination file system on copy

#       \--no-unicode-normalization                            Don't normalize unicode characters in filenames

#       \--no-update-dir-modtime                               Don't update directory modification times

#       \--no-update-modtime                                   Don't update destination modtime if files identical

#   \-x, \--one-file-system                                     Don't cross filesystem boundaries (unix/macOS only)

#       \--onedrive-access-scopes SpaceSepList                 Set scopes to be requested by rclone (default Files.Read Files.ReadWrite Files.Read.All Files.ReadWrite.All Sites.Read.All offline\_access)

#       \--onedrive-auth-url string                            Auth server URL

#       \--onedrive-av-override                                Allows download of files the server thinks has a virus

#       \--onedrive-chunk-size SizeSuffix                      Chunk size to upload files with \- must be multiple of 320k (327,680 bytes) (default 10Mi)

#       \--onedrive-client-credentials                         Use client credentials OAuth flow

#       \--onedrive-client-id string                           OAuth Client Id

#       \--onedrive-client-secret string                       OAuth Client Secret

#       \--onedrive-delta                                      If set rclone will use delta listing to implement recursive listings

#       \--onedrive-description string                         Description of the remote

#       \--onedrive-drive-id string                            The ID of the drive to use

#       \--onedrive-drive-type string                          The type of the drive (personal | business | documentLibrary)

#       \--onedrive-encoding Encoding                          The encoding for the backend (default Slash,LtGt,DoubleQuote,Colon,Question,Asterisk,Pipe,BackSlash,Del,Ctl,LeftSpace,LeftTilde,RightSpace,RightPeriod,InvalidUtf8,Dot)

#       \--onedrive-expose-onenote-files                       Set to make OneNote files show up in directory listings

#       \--onedrive-hard-delete                                Permanently delete files on removal

#       \--onedrive-hash-type string                           Specify the hash in use for the backend (default "auto")

#       \--onedrive-link-password string                       Set the password for links created by the link command

#       \--onedrive-link-scope string                          Set the scope of the links created by the link command (default "anonymous")

#       \--onedrive-link-type string                           Set the type of the links created by the link command (default "view")

#       \--onedrive-list-chunk int                             Size of listing chunk (default 1000\)

#       \--onedrive-metadata-permissions Bits                  Control whether permissions should be read or written in metadata (default off)

#       \--onedrive-no-versions                                Remove all versions on modifying operations

#       \--onedrive-region string                              Choose national cloud region for OneDrive (default "global")

#       \--onedrive-root-folder-id string                      ID of the root folder

#       \--onedrive-server-side-across-configs                 Deprecated: use \--server-side-across-configs instead

#       \--onedrive-tenant string                              ID of the service principal's tenant. Also called its directory ID

#       \--onedrive-token string                               OAuth Access Token as a JSON blob

#       \--onedrive-token-url string                           Token server url

#       \--onedrive-upload-cutoff SizeSuffix                   Cutoff for switching to chunked upload (default off)

#       \--oos-attempt-resume-upload                           If true attempt to resume previously started multipart upload for the object

#       \--oos-chunk-size SizeSuffix                           Chunk size to use for uploading (default 5Mi)

#       \--oos-compartment string                              Specify compartment OCID, if you need to list buckets

#       \--oos-config-file string                              Path to OCI config file (default "\~/.oci/config")

#       \--oos-config-profile string                           Profile name inside the oci config file (default "Default")

#       \--oos-copy-cutoff SizeSuffix                          Cutoff for switching to multipart copy (default 4.656Gi)

#       \--oos-copy-timeout Duration                           Timeout for copy (default 1m0s)

#       \--oos-description string                              Description of the remote

#       \--oos-disable-checksum                                Don't store MD5 checksum with object metadata

#       \--oos-encoding Encoding                               The encoding for the backend (default Slash,InvalidUtf8,Dot)

#       \--oos-endpoint string                                 Endpoint for Object storage API

#       \--oos-leave-parts-on-error                            If true avoid calling abort upload on a failure, leaving all successfully uploaded parts for manual recovery

#       \--oos-max-upload-parts int                            Maximum number of parts in a multipart upload (default 10000\)

#       \--oos-namespace string                                Object storage namespace

#       \--oos-no-check-bucket                                 If set, don't attempt to check the bucket exists or create it

#       \--oos-provider string                                 Choose your Auth Provider (default "env\_auth")

#       \--oos-region string                                   Object storage Region

#       \--oos-sse-customer-algorithm string                   If using SSE-C, the optional header that specifies "AES256" as the encryption algorithm

#       \--oos-sse-customer-key string                         To use SSE-C, the optional header that specifies the base64-encoded 256-bit encryption key to use to

#       \--oos-sse-customer-key-file string                    To use SSE-C, a file containing the base64-encoded string of the AES-256 encryption key associated

#       \--oos-sse-customer-key-sha256 string                  If using SSE-C, The optional header that specifies the base64-encoded SHA256 hash of the encryption

#       \--oos-sse-kms-key-id string                           if using your own master key in vault, this header specifies the

#       \--oos-storage-tier string                             The storage class to use when storing new objects in storage. https://docs.oracle.com/en-us/iaas/Content/Object/Concepts/understandingstoragetiers.htm (default "Standard")

#       \--oos-upload-concurrency int                          Concurrency for multipart uploads (default 10\)

#       \--oos-upload-cutoff SizeSuffix                        Cutoff for switching to chunked upload (default 200Mi)

#       \--opendrive-access string                             Files and folders will be uploaded with this access permission (default private) (default "private")

#       \--opendrive-chunk-size SizeSuffix                     Files will be uploaded in chunks this size (default 10Mi)

#       \--opendrive-description string                        Description of the remote

#       \--opendrive-encoding Encoding                         The encoding for the backend (default Slash,LtGt,DoubleQuote,Colon,Question,Asterisk,Pipe,BackSlash,LeftSpace,LeftCrLfHtVt,RightSpace,RightCrLfHtVt,InvalidUtf8,Dot)

#       \--opendrive-password string                           Password (obscured)

#       \--opendrive-username string                           Username

#       \--order-by string                                     Instructions on how to order the transfers, e.g. 'size,descending'

#       \--partial-suffix string                               Add partial-suffix to temporary file name when \--inplace is not used (default ".partial")

#       \--password-command SpaceSepList                       Command for supplying password for encrypted configuration

#       \--pcloud-auth-url string                              Auth server URL

#       \--pcloud-client-credentials                           Use client credentials OAuth flow

#       \--pcloud-client-id string                             OAuth Client Id

#       \--pcloud-client-secret string                         OAuth Client Secret

#       \--pcloud-description string                           Description of the remote

#       \--pcloud-encoding Encoding                            The encoding for the backend (default Slash,BackSlash,Del,Ctl,InvalidUtf8,Dot)

#       \--pcloud-hostname string                              Hostname to connect to (default "api.pcloud.com")

#       \--pcloud-password string                              Your pcloud password (obscured)

#       \--pcloud-root-folder-id string                        Fill in for rclone to use a non root folder as its starting point (default "d0")

#       \--pcloud-token string                                 OAuth Access Token as a JSON blob

#       \--pcloud-token-url string                             Token server url

#       \--pcloud-username string                              Your pcloud username

#       \--pikpak-chunk-size SizeSuffix                        Chunk size for multipart uploads (default 5Mi)

#       \--pikpak-description string                           Description of the remote

#       \--pikpak-device-id string                             Device ID used for authorization

#       \--pikpak-encoding Encoding                            The encoding for the backend (default Slash,LtGt,DoubleQuote,Colon,Question,Asterisk,Pipe,BackSlash,Ctl,LeftSpace,RightSpace,RightPeriod,InvalidUtf8,Dot)

#       \--pikpak-hash-memory-limit SizeSuffix                 Files bigger than this will be cached on disk to calculate hash if required (default 10Mi)

#       \--pikpak-no-media-link                                Use original file links instead of media links

#       \--pikpak-pass string                                  Pikpak password (obscured)

#       \--pikpak-root-folder-id string                        ID of the root folder

#       \--pikpak-trashed-only                                 Only show files that are in the trash

#       \--pikpak-upload-concurrency int                       Concurrency for multipart uploads (default 4\)

#       \--pikpak-upload-cutoff SizeSuffix                     Cutoff for switching to chunked upload (default 200Mi)

#       \--pikpak-use-trash                                    Send files to the trash instead of deleting permanently (default true)

#       \--pikpak-user string                                  Pikpak username

#       \--pikpak-user-agent string                            HTTP user agent for pikpak (default "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0")

#       \--pixeldrain-api-key string                           API key for your pixeldrain account

#       \--pixeldrain-api-url string                           The API endpoint to connect to. In the vast majority of cases it's fine to leave (default "https://pixeldrain.com/api")

#       \--pixeldrain-description string                       Description of the remote

#       \--pixeldrain-root-folder-id string                    Root of the filesystem to use (default "me")

#       \--premiumizeme-auth-url string                        Auth server URL

#       \--premiumizeme-client-credentials                     Use client credentials OAuth flow

#       \--premiumizeme-client-id string                       OAuth Client Id

#       \--premiumizeme-client-secret string                   OAuth Client Secret

#       \--premiumizeme-description string                     Description of the remote

#       \--premiumizeme-encoding Encoding                      The encoding for the backend (default Slash,DoubleQuote,BackSlash,Del,Ctl,InvalidUtf8,Dot)

#       \--premiumizeme-token string                           OAuth Access Token as a JSON blob

#       \--premiumizeme-token-url string                       Token server url

#   \-P, \--progress                                            Show progress during transfer

#       \--progress-terminal-title                             Show progress on the terminal title (requires \-P/--progress)

#       \--protondrive-2fa string                              The 2FA code

#       \--protondrive-app-version string                      The app version string (default "macos-drive@1.0.0-alpha.1+rclone")

#       \--protondrive-description string                      Description of the remote

#       \--protondrive-enable-caching                          Caches the files and folders metadata to reduce API calls (default true)

#       \--protondrive-encoding Encoding                       The encoding for the backend (default Slash,LeftSpace,RightSpace,InvalidUtf8,Dot)

#       \--protondrive-mailbox-password string                 The mailbox password of your two-password proton account (obscured)

#       \--protondrive-original-file-size                      Return the file size before encryption (default true)

#       \--protondrive-otp-secret-key string                   The OTP secret key (obscured)

#       \--protondrive-password string                         The password of your proton account (obscured)

#       \--protondrive-replace-existing-draft                  Create a new revision when filename conflict is detected

#       \--protondrive-username string                         The username of your proton account

#       \--putio-auth-url string                               Auth server URL

#       \--putio-client-credentials                            Use client credentials OAuth flow

#       \--putio-client-id string                              OAuth Client Id

#       \--putio-client-secret string                          OAuth Client Secret

#       \--putio-description string                            Description of the remote

#       \--putio-encoding Encoding                             The encoding for the backend (default Slash,BackSlash,Del,Ctl,InvalidUtf8,Dot)

#       \--putio-token string                                  OAuth Access Token as a JSON blob

#       \--putio-token-url string                              Token server url

#       \--qingstor-access-key-id string                       QingStor Access Key ID

#       \--qingstor-chunk-size SizeSuffix                      Chunk size to use for uploading (default 4Mi)

#       \--qingstor-connection-retries int                     Number of connection retries (default 3\)

#       \--qingstor-description string                         Description of the remote

#       \--qingstor-encoding Encoding                          The encoding for the backend (default Slash,Ctl,InvalidUtf8)

#       \--qingstor-endpoint string                            Enter an endpoint URL to connection QingStor API

#       \--qingstor-env-auth                                   Get QingStor credentials from runtime

#       \--qingstor-secret-access-key string                   QingStor Secret Access Key (password)

#       \--qingstor-upload-concurrency int                     Concurrency for multipart uploads (default 1\)

#       \--qingstor-upload-cutoff SizeSuffix                   Cutoff for switching to chunked upload (default 200Mi)

#       \--qingstor-zone string                                Zone to connect to

#       \--quatrix-api-key string                              API key for accessing Quatrix account

#       \--quatrix-description string                          Description of the remote

#       \--quatrix-effective-upload-time string                Wanted upload time for one chunk (default "4s")

#       \--quatrix-encoding Encoding                           The encoding for the backend (default Slash,BackSlash,Del,Ctl,InvalidUtf8,Dot)

#       \--quatrix-hard-delete                                 Delete files permanently rather than putting them into the trash

#       \--quatrix-host string                                 Host name of Quatrix account

#       \--quatrix-maximal-summary-chunk-size SizeSuffix       The maximal summary for all chunks. It should not be less than 'transfers'\*'minimal\_chunk\_size' (default 95.367Mi)

#       \--quatrix-minimal-chunk-size SizeSuffix               The minimal size for one chunk (default 9.537Mi)

#       \--quatrix-skip-project-folders                        Skip project folders in operations

#   \-q, \--quiet                                               Print as little stuff as possible

#       \--rc                                                  Enable the remote control server

#       \--rc-addr stringArray                                 IPaddress:Port or :Port to bind server to (default localhost:5572)

#       \--rc-allow-origin string                              Origin which cross-domain request (CORS) can be executed from

#       \--rc-baseurl string                                   Prefix for URLs \- leave blank for root

#       \--rc-cert string                                      TLS PEM key (concatenation of certificate and CA certificate)

#       \--rc-client-ca string                                 Client certificate authority to verify clients with

#       \--rc-enable-metrics                                   Enable the Prometheus metrics path at the remote control server

#       \--rc-files string                                     Path to local files to serve on the HTTP server

#       \--rc-htpasswd string                                  A htpasswd file \- if not provided no authentication is done

#       \--rc-job-expire-duration Duration                     Expire finished async jobs older than this value (default 1m0s)

#       \--rc-job-expire-interval Duration                     Interval to check for expired async jobs (default 10s)

#       \--rc-key string                                       TLS PEM Private key

#       \--rc-max-header-bytes int                             Maximum size of request header (default 4096\)

#       \--rc-min-tls-version string                           Minimum TLS version that is acceptable (default "tls1.0")

#       \--rc-no-auth                                          Don't require auth for certain methods

#       \--rc-pass string                                      Password for authentication

#       \--rc-realm string                                     Realm for authentication

#       \--rc-salt string                                      Password hashing salt (default "dlPL2MqE")

#       \--rc-serve                                            Enable the serving of remote objects

#       \--rc-serve-no-modtime                                 Don't read the modification time (can speed things up)

#       \--rc-server-read-timeout Duration                     Timeout for server reading data (default 1h0m0s)

#       \--rc-server-write-timeout Duration                    Timeout for server writing data (default 1h0m0s)

#       \--rc-template string                                  User-specified template

#       \--rc-user string                                      User name for authentication

#       \--rc-user-from-header string                          User name from a defined HTTP header

#       \--rc-web-fetch-url string                             URL to fetch the releases for webgui (default "https://api.github.com/repos/rclone/rclone-webui-react/releases/latest")

#       \--rc-web-gui                                          Launch WebGUI on localhost

#       \--rc-web-gui-force-update                             Force update to latest version of web gui

#       \--rc-web-gui-no-open-browser                          Don't open the browser automatically

#       \--rc-web-gui-update                                   Check and update to latest version of web gui

#       \--refresh-times                                       Refresh the modtime of remote files

#       \--retries int                                         Retry operations this many times if they fail (default 3\)

#       \--retries-sleep Duration                              Interval between retrying operations if they fail, e.g. 500ms, 60s, 5m (0 to disable) (default 0s)

#       \--s3-access-key-id string                             AWS Access Key ID

#       \--s3-acl string                                       Canned ACL used when creating buckets and storing or copying objects

#       \--s3-bucket-acl string                                Canned ACL used when creating buckets

#       \--s3-chunk-size SizeSuffix                            Chunk size to use for uploading (default 5Mi)

#       \--s3-copy-cutoff SizeSuffix                           Cutoff for switching to multipart copy (default 4.656Gi)

#       \--s3-decompress                                       If set this will decompress gzip encoded objects

#       \--s3-description string                               Description of the remote

#       \--s3-directory-bucket                                 Set to use AWS Directory Buckets

#       \--s3-directory-markers                                Upload an empty object with a trailing slash when a new directory is created

#       \--s3-disable-checksum                                 Don't store MD5 checksum with object metadata

#       \--s3-disable-http2                                    Disable usage of http2 for S3 backends

#       \--s3-download-url string                              Custom endpoint for downloads

#       \--s3-encoding Encoding                                The encoding for the backend (default Slash,InvalidUtf8,Dot)

#       \--s3-endpoint string                                  Endpoint for S3 API

#       \--s3-env-auth                                         Get AWS credentials from runtime (environment variables or EC2/ECS meta data if no env vars)

#       \--s3-force-path-style                                 If true use path style access if false use virtual hosted style (default true)

#       \--s3-ibm-api-key string                               IBM API Key to be used to obtain IAM token

#       \--s3-ibm-resource-instance-id string                  IBM service instance id

#       \--s3-leave-parts-on-error                             If true avoid calling abort upload on a failure, leaving all successfully uploaded parts on S3 for manual recovery

#       \--s3-list-chunk int                                   Size of listing chunk (response list for each ListObject S3 request) (default 1000\)

#       \--s3-list-url-encode Tristate                         Whether to url encode listings: true/false/unset (default unset)

#       \--s3-list-version int                                 Version of ListObjects to use: 1,2 or 0 for auto

#       \--s3-location-constraint string                       Location constraint \- must be set to match the Region

#       \--s3-max-upload-parts int                             Maximum number of parts in a multipart upload (default 10000\)

#       \--s3-might-gzip Tristate                              Set this if the backend might gzip objects (default unset)

#       \--s3-no-check-bucket                                  If set, don't attempt to check the bucket exists or create it

#       \--s3-no-head                                          If set, don't HEAD uploaded objects to check integrity

#       \--s3-no-head-object                                   If set, do not do HEAD before GET when getting objects

#       \--s3-no-system-metadata                               Suppress setting and reading of system metadata

#       \--s3-profile string                                   Profile to use in the shared credentials file

#       \--s3-provider string                                  Choose your S3 provider

#       \--s3-region string                                    Region to connect to

#       \--s3-requester-pays                                   Enables requester pays option when interacting with S3 bucket

#       \--s3-role-arn string                                  ARN of the IAM role to assume

#       \--s3-role-external-id string                          External ID for assumed role

#       \--s3-role-session-duration string                     Session duration for assumed role

#       \--s3-role-session-name string                         Session name for assumed role

#       \--s3-sdk-log-mode Bits                                Set to debug the SDK (default Off)

#       \--s3-secret-access-key string                         AWS Secret Access Key (password)

#       \--s3-server-side-encryption string                    The server-side encryption algorithm used when storing this object in S3

#       \--s3-session-token string                             An AWS session token

#       \--s3-shared-credentials-file string                   Path to the shared credentials file

#       \--s3-sign-accept-encoding Tristate                    Set if rclone should include Accept-Encoding as part of the signature (default unset)

#       \--s3-sse-customer-algorithm string                    If using SSE-C, the server-side encryption algorithm used when storing this object in S3

#       \--s3-sse-customer-key string                          To use SSE-C you may provide the secret encryption key used to encrypt/decrypt your data

#       \--s3-sse-customer-key-base64 string                   If using SSE-C you must provide the secret encryption key encoded in base64 format to encrypt/decrypt your data

#       \--s3-sse-customer-key-md5 string                      If using SSE-C you may provide the secret encryption key MD5 checksum (optional)

#       \--s3-sse-kms-key-id string                            If using KMS ID you must provide the ARN of Key

#       \--s3-storage-class string                             The storage class to use when storing new objects in S3

#       \--s3-upload-concurrency int                           Concurrency for multipart uploads and copies (default 4\)

#       \--s3-upload-cutoff SizeSuffix                         Cutoff for switching to chunked upload (default 200Mi)

#       \--s3-use-accelerate-endpoint                          If true use the AWS S3 accelerated endpoint

#       \--s3-use-accept-encoding-gzip Accept-Encoding: gzip   Whether to send Accept-Encoding: gzip header (default unset)

#       \--s3-use-already-exists Tristate                      Set if rclone should report BucketAlreadyExists errors on bucket creation (default unset)

#       \--s3-use-arn-region                                   If true, enables arn region support for the service

#       \--s3-use-data-integrity-protections Tristate          If true use AWS S3 data integrity protections (default unset)

#       \--s3-use-dual-stack                                   If true use AWS S3 dual-stack endpoint (IPv6 support)

#       \--s3-use-multipart-etag Tristate                      Whether to use ETag in multipart uploads for verification (default unset)

#       \--s3-use-multipart-uploads Tristate                   Set if rclone should use multipart uploads (default unset)

#       \--s3-use-presigned-request                            Whether to use a presigned request or PutObject for single part uploads

#       \--s3-use-unsigned-payload Tristate                    Whether to use an unsigned payload in PutObject (default unset)

#       \--s3-use-x-id Tristate                                Set if rclone should add x-id URL parameters (default unset)

#       \--s3-v2-auth                                          If true use v2 authentication

#       \--s3-version-at Time                                  Show file versions as they were at the specified time (default off)

#       \--s3-version-deleted                                  Show deleted file markers when using versions

#       \--s3-versions                                         Include old versions in directory listings

#       \--seafile-2fa                                         Two-factor authentication ('true' if the account has 2FA enabled)

#       \--seafile-create-library                              Should rclone create a library if it doesn't exist

#       \--seafile-description string                          Description of the remote

#       \--seafile-encoding Encoding                           The encoding for the backend (default Slash,DoubleQuote,BackSlash,Ctl,InvalidUtf8,Dot)

#       \--seafile-library string                              Name of the library

#       \--seafile-library-key string                          Library password (for encrypted libraries only) (obscured)

#       \--seafile-pass string                                 Password (obscured)

#       \--seafile-url string                                  URL of seafile host to connect to

#       \--seafile-user string                                 User name (usually email address)

#       \--server-side-across-configs                          Allow server-side operations (e.g. copy) to work across different configs

#       \--sftp-ask-password                                   Allow asking for SFTP password when needed

#       \--sftp-blake3sum-command string                       The command used to read BLAKE3 hashes

#       \--sftp-chunk-size SizeSuffix                          Upload and download chunk size (default 32Ki)

#       \--sftp-ciphers SpaceSepList                           Space separated list of ciphers to be used for session encryption, ordered by preference

#       \--sftp-concurrency int                                The maximum number of outstanding requests for one file (default 64\)

#       \--sftp-connections int                                Maximum number of SFTP simultaneous connections, 0 for unlimited

#       \--sftp-copy-is-hardlink                               Set to enable server side copies using hardlinks

#       \--sftp-crc32sum-command string                        The command used to read CRC-32 hashes

#       \--sftp-description string                             Description of the remote

#       \--sftp-disable-concurrent-reads                       If set don't use concurrent reads

#       \--sftp-disable-concurrent-writes                      If set don't use concurrent writes

#       \--sftp-disable-hashcheck                              Disable the execution of SSH commands to determine if remote file hashing is available

#       \--sftp-hashes CommaSepList                            Comma separated list of supported checksum types

#       \--sftp-host string                                    SSH host to connect to

#       \--sftp-host-key-algorithms SpaceSepList               Space separated list of host key algorithms, ordered by preference

#       \--sftp-http-proxy string                              URL for HTTP CONNECT proxy

#       \--sftp-idle-timeout Duration                          Max time before closing idle connections (default 1m0s)

#       \--sftp-key-exchange SpaceSepList                      Space separated list of key exchange algorithms, ordered by preference

#       \--sftp-key-file string                                Path to PEM-encoded private key file

#       \--sftp-key-file-pass string                           The passphrase to decrypt the PEM-encoded private key file (obscured)

#       \--sftp-key-pem string                                 Raw PEM-encoded private key

#       \--sftp-key-use-agent                                  When set forces the usage of the ssh-agent

#       \--sftp-known-hosts-file string                        Optional path to known\_hosts file

#       \--sftp-macs SpaceSepList                              Space separated list of MACs (message authentication code) algorithms, ordered by preference

#       \--sftp-md5sum-command string                          The command used to read MD5 hashes

#       \--sftp-pass string                                    SSH password, leave blank to use ssh-agent (obscured)

#       \--sftp-path-override string                           Override path used by SSH shell commands

#       \--sftp-port int                                       SSH port number (default 22\)

#       \--sftp-pubkey string                                  SSH public certificate for public certificate based authentication

#       \--sftp-pubkey-file string                             Optional path to public key file

#       \--sftp-server-command string                          Specifies the path or command to run a sftp server on the remote host

#       \--sftp-set-env SpaceSepList                           Environment variables to pass to sftp and commands

#       \--sftp-set-modtime                                    Set the modified time on the remote if set (default true)

#       \--sftp-sha1sum-command string                         The command used to read SHA-1 hashes

#       \--sftp-sha256sum-command string                       The command used to read SHA-256 hashes

#       \--sftp-shell-type string                              The type of SSH shell on remote server, if any

#       \--sftp-skip-links                                     Set to skip any symlinks and any other non regular files

#       \--sftp-socks-proxy string                             Socks 5 proxy host

#       \--sftp-ssh SpaceSepList                               Path and arguments to external ssh binary

#       \--sftp-subsystem string                               Specifies the SSH2 subsystem on the remote host (default "sftp")

#       \--sftp-use-fstat                                      If set use fstat instead of stat

#       \--sftp-use-insecure-cipher                            Enable the use of insecure ciphers and key exchange methods

#       \--sftp-user string                                    SSH username (default "$USER")

#       \--sftp-xxh128sum-command string                       The command used to read XXH128 hashes

#       \--sftp-xxh3sum-command string                         The command used to read XXH3 hashes

#       \--shade-api-key string                                An API key for your account

#       \--shade-chunk-size SizeSuffix                         Chunk size to use for uploading (default 64Mi)

#       \--shade-description string                            Description of the remote

#       \--shade-drive-id string                               The ID of your drive, see this in the drive settings. Individual rclone configs must be made per drive

#       \--shade-encoding Encoding                             The encoding for the backend (default Slash,BackSlash,Del,Ctl,InvalidUtf8,Dot)

#       \--shade-endpoint string                               Endpoint for the service

#       \--shade-max-upload-parts int                          Maximum amount of parts in a multipart upload (default 10000\)

#       \--shade-token string                                  JWT Token for performing Shade FS operations. Don't set this value \- rclone will set it automatically

#       \--shade-token-expiry string                           JWT Token Expiration time. Don't set this value \- rclone will set it automatically

#       \--shade-upload-concurrency int                        Concurrency for multipart uploads and copies. This is the number of chunks of the same file that are uploaded concurrently for multipart uploads and copies (default 4\)

#       \--sharefile-auth-url string                           Auth server URL

#       \--sharefile-chunk-size SizeSuffix                     Upload chunk size (default 64Mi)

#       \--sharefile-client-credentials                        Use client credentials OAuth flow

#       \--sharefile-client-id string                          OAuth Client Id

#       \--sharefile-client-secret string                      OAuth Client Secret

#       \--sharefile-description string                        Description of the remote

#       \--sharefile-encoding Encoding                         The encoding for the backend (default Slash,LtGt,DoubleQuote,Colon,Question,Asterisk,Pipe,BackSlash,Ctl,LeftSpace,LeftPeriod,RightSpace,RightPeriod,InvalidUtf8,Dot)

#       \--sharefile-endpoint string                           Endpoint for API calls

#       \--sharefile-root-folder-id string                     ID of the root folder

#       \--sharefile-token string                              OAuth Access Token as a JSON blob

#       \--sharefile-token-url string                          Token server url

#       \--sharefile-upload-cutoff SizeSuffix                  Cutoff for switching to multipart upload (default 128Mi)

#       \--sia-api-password string                             Sia Daemon API Password (obscured)

#       \--sia-api-url string                                  Sia daemon API URL, like http://sia.daemon.host:9980 (default "http://127.0.0.1:9980")

#       \--sia-description string                              Description of the remote

#       \--sia-encoding Encoding                               The encoding for the backend (default Slash,Question,Hash,Percent,Del,Ctl,InvalidUtf8,Dot)

#       \--sia-user-agent string                               Siad User Agent (default "Sia-Agent")

#       \--size-only                                           Skip based on size only, not modtime or checksum

#       \--skip-links                                          Don't warn about skipped symlinks

#       \--skip-specials                                       Don't warn about skipped pipes, sockets and device objects

#       \--smb-case-insensitive                                Whether the server is configured to be case-insensitive (default true)

#       \--smb-description string                              Description of the remote

#       \--smb-domain string                                   Domain name for NTLM authentication (default "WORKGROUP")

#       \--smb-encoding Encoding                               The encoding for the backend (default Slash,LtGt,DoubleQuote,Colon,Question,Asterisk,Pipe,BackSlash,Ctl,RightSpace,RightPeriod,InvalidUtf8,Dot)

#       \--smb-hide-special-share                              Hide special shares (e.g. print$) which users aren't supposed to access (default true)

#       \--smb-host string                                     SMB server hostname to connect to

#       \--smb-idle-timeout Duration                           Max time before closing idle connections (default 1m0s)

#       \--smb-kerberos-ccache string                          Path to the Kerberos credential cache (krb5cc)

#       \--smb-pass string                                     SMB password (obscured)

#       \--smb-port int                                        SMB port number (default 445\)

#       \--smb-spn string                                      Service principal name

#       \--smb-use-kerberos                                    Use Kerberos authentication

#       \--smb-user string                                     SMB username (default "$USER")

#       \--stats Duration                                      Interval between printing stats, e.g. 500ms, 60s, 5m (0 to disable) (default 1m0s)

#       \--stats-file-name-length int                          Max file name length in stats (0 for no limit) (default 45\)

#       \--stats-log-level LogLevel                            Log level to show \--stats output DEBUG|INFO|NOTICE|ERROR (default INFO)

#       \--stats-one-line                                      Make the stats fit on one line

#       \--stats-one-line-date                                 Enable \--stats-one-line and add current date/time prefix

#       \--stats-one-line-date-format string                   Enable \--stats-one-line-date and use custom formatted date: Enclose date string in double quotes ("), see https://golang.org/pkg/time/\#Time.Format

#       \--stats-unit string                                   Show data rate in stats as either 'bits' or 'bytes' per second (default "bytes")

#       \--storj-access-grant string                           Access grant

#       \--storj-api-key string                                API key

#       \--storj-description string                            Description of the remote

#       \--storj-passphrase string                             Encryption passphrase

#       \--storj-provider string                               Choose an authentication method (default "existing")

#       \--storj-satellite-address string                      Satellite address (default "us1.storj.io")

#       \--streaming-upload-cutoff SizeSuffix                  Cutoff for switching to chunked upload if file size is unknown, upload starts after reaching cutoff or when file ends (default 100Ki)

#       \--suffix string                                       Suffix to add to changed files

#       \--suffix-keep-extension                               Preserve the extension when using \--suffix

#       \--sugarsync-access-key-id string                      Sugarsync Access Key ID

#       \--sugarsync-app-id string                             Sugarsync App ID

#       \--sugarsync-authorization string                      Sugarsync authorization

#       \--sugarsync-authorization-expiry string               Sugarsync authorization expiry

#       \--sugarsync-deleted-id string                         Sugarsync deleted folder id

#       \--sugarsync-description string                        Description of the remote

#       \--sugarsync-encoding Encoding                         The encoding for the backend (default Slash,Ctl,InvalidUtf8,Dot)

#       \--sugarsync-hard-delete                               Permanently delete files if true

#       \--sugarsync-private-access-key string                 Sugarsync Private Access Key

#       \--sugarsync-refresh-token string                      Sugarsync refresh token

#       \--sugarsync-root-id string                            Sugarsync root id

#       \--sugarsync-user string                               Sugarsync user

#       \--swift-application-credential-id string              Application Credential ID (OS\_APPLICATION\_CREDENTIAL\_ID)

#       \--swift-application-credential-name string            Application Credential Name (OS\_APPLICATION\_CREDENTIAL\_NAME)

#       \--swift-application-credential-secret string          Application Credential Secret (OS\_APPLICATION\_CREDENTIAL\_SECRET)

#       \--swift-auth string                                   Authentication URL for server (OS\_AUTH\_URL)

#       \--swift-auth-token string                             Auth Token from alternate authentication \- optional (OS\_AUTH\_TOKEN)

#       \--swift-auth-version int                              AuthVersion \- optional \- set to (1,2,3) if your auth URL has no version (ST\_AUTH\_VERSION)

#       \--swift-chunk-size SizeSuffix                         Above this size files will be chunked (default 5Gi)

#       \--swift-description string                            Description of the remote

#       \--swift-domain string                                 User domain \- optional (v3 auth) (OS\_USER\_DOMAIN\_NAME)

#       \--swift-encoding Encoding                             The encoding for the backend (default Slash,InvalidUtf8)

#       \--swift-endpoint-type string                          Endpoint type to choose from the service catalogue (OS\_ENDPOINT\_TYPE) (default "public")

#       \--swift-env-auth                                      Get swift credentials from environment variables in standard OpenStack form

#       \--swift-fetch-until-empty-page                        When paginating, always fetch unless we received an empty page

#       \--swift-key string                                    API key or password (OS\_PASSWORD)

#       \--swift-leave-parts-on-error                          If true avoid calling abort upload on a failure

#       \--swift-no-chunk                                      Don't chunk files during streaming upload

#       \--swift-no-large-objects                              Disable support for static and dynamic large objects

#       \--swift-partial-page-fetch-threshold int              When paginating, fetch if the current page is within this percentage of the limit

#       \--swift-region string                                 Region name \- optional (OS\_REGION\_NAME)

#       \--swift-storage-policy string                         The storage policy to use when creating a new container

#       \--swift-storage-url string                            Storage URL \- optional (OS\_STORAGE\_URL)

#       \--swift-tenant string                                 Tenant name \- optional for v1 auth, this or tenant\_id required otherwise (OS\_TENANT\_NAME or OS\_PROJECT\_NAME)

#       \--swift-tenant-domain string                          Tenant domain \- optional (v3 auth) (OS\_PROJECT\_DOMAIN\_NAME)

#       \--swift-tenant-id string                              Tenant ID \- optional for v1 auth, this or tenant required otherwise (OS\_TENANT\_ID)

#       \--swift-use-segments-container Tristate               Choose destination for large object segments (default unset)

#       \--swift-user string                                   User name to log in (OS\_USERNAME)

#       \--swift-user-id string                                User ID to log in \- optional \- most swift systems use user and leave this blank (v3 auth) (OS\_USER\_ID)

#       \--syslog                                              Use Syslog for logging

#       \--syslog-facility string                              Facility for syslog, e.g. KERN,USER (default "DAEMON")

#       \--temp-dir string                                     Directory rclone will use for temporary files (default "/tmp")

#       \--timeout Duration                                    IO idle timeout (default 5m0s)

#       \--tpslimit float                                      Limit HTTP transactions per second to this

#       \--tpslimit-burst int                                  Max burst of transactions for \--tpslimit (default 1\)

#       \--track-renames                                       When synchronizing, track file renames and do a server-side move if possible

#       \--track-renames-strategy string                       Strategies to use when synchronizing using track-renames hash|modtime|leaf (default "hash")

#       \--transfers int                                       Number of file transfers to run in parallel (default 4\)

#       \--ulozto-app-token string                             The application token identifying the app. An app API key can be either found in the API

#       \--ulozto-description string                           Description of the remote

#       \--ulozto-encoding Encoding                            The encoding for the backend (default Slash,BackSlash,Del,Ctl,InvalidUtf8,Dot)

#       \--ulozto-list-page-size int                           The size of a single page for list commands. 1-500 (default 500\)

#       \--ulozto-password string                              The password for the user (obscured)

#       \--ulozto-root-folder-slug string                      If set, rclone will use this folder as the root folder for all operations. For example,

#       \--ulozto-username string                              The username of the principal to operate as

#       \--union-action-policy string                          Policy to choose upstream on ACTION category (default "epall")

#       \--union-cache-time int                                Cache time of usage and free space (in seconds) (default 120\)

#       \--union-create-policy string                          Policy to choose upstream on CREATE category (default "epmfs")

#       \--union-description string                            Description of the remote

#       \--union-min-free-space SizeSuffix                     Minimum viable free space for lfs/eplfs policies (default 1Gi)

#       \--union-search-policy string                          Policy to choose upstream on SEARCH category (default "ff")

#       \--union-upstreams string                              List of space separated upstreams

#   \-u, \--update                                              Skip files that are newer on the destination

#       \--use-cookies                                         Enable session cookiejar

#       \--use-json-log                                        Use json log format

#       \--use-mmap                                            Use mmap allocator (see docs)

#       \--use-server-modtime                                  Use server modified time instead of object metadata

#       \--user-agent string                                   Set the user-agent to a specified string (default "rclone/v1.73.2")

#   \-v, \--verbose count                                       Print lots more stuff (repeat for more)

#   \-V, \--version                                             Print the version number

#       \--webdav-auth-redirect                                Preserve authentication on redirect

#       \--webdav-bearer-token string                          Bearer token instead of user/pass (e.g. a Macaroon)

#       \--webdav-bearer-token-command string                  Command to run to get a bearer token

#       \--webdav-description string                           Description of the remote

#       \--webdav-encoding string                              The encoding for the backend

#       \--webdav-headers CommaSepList                         Set HTTP headers for all transactions

#       \--webdav-nextcloud-chunk-size SizeSuffix              Nextcloud upload chunk size (default 10Mi)

#       \--webdav-owncloud-exclude-mounts                      Exclude ownCloud mounted storages

#       \--webdav-owncloud-exclude-shares                      Exclude ownCloud shares

#       \--webdav-pacer-min-sleep Duration                     Minimum time to sleep between API calls (default 10ms)

#       \--webdav-pass string                                  Password (obscured)

#       \--webdav-unix-socket string                           Path to a unix domain socket to dial to, instead of opening a TCP connection directly

#       \--webdav-url string                                   URL of http host to connect to

#       \--webdav-user string                                  User name

#       \--webdav-vendor string                                Name of the WebDAV site/service/software you are using

#       \--yandex-auth-url string                              Auth server URL

#       \--yandex-client-credentials                           Use client credentials OAuth flow

#       \--yandex-client-id string                             OAuth Client Id

#       \--yandex-client-secret string                         OAuth Client Secret

#       \--yandex-description string                           Description of the remote

#       \--yandex-encoding Encoding                            The encoding for the backend (default Slash,Del,Ctl,InvalidUtf8,Dot)

#       \--yandex-hard-delete                                  Delete files permanently rather than putting them into the trash

#       \--yandex-spoof-ua                                     Set the user agent to match an official version of the yandex disk client. May help with upload performance (default true)

#       \--yandex-token string                                 OAuth Access Token as a JSON blob

#       \--yandex-token-url string                             Token server url

#       \--zoho-auth-url string                                Auth server URL

#       \--zoho-client-credentials                             Use client credentials OAuth flow

#       \--zoho-client-id string                               OAuth Client Id

#       \--zoho-client-secret string                           OAuth Client Secret

#       \--zoho-description string                             Description of the remote

#       \--zoho-encoding Encoding                              The encoding for the backend (default Del,Ctl,InvalidUtf8)

#       \--zoho-region string                                  Zoho region to connect to

#       \--zoho-token string                                   OAuth Access Token as a JSON blob

#       \--zoho-token-url string                               Token server url

#       \--zoho-upload-cutoff SizeSuffix                       Cutoff for switching to large file upload api (\>= 10 MiB) (default 10Mi)

# 

## See Also

* # [rclone about](https://rclone.org/commands/rclone_about/) \- Get quota information from the remote.

* # [rclone archive](https://rclone.org/commands/rclone_archive/) \- Perform an action on an archive.

* # [rclone authorize](https://rclone.org/commands/rclone_authorize/) \- Remote authorization.

* # [rclone backend](https://rclone.org/commands/rclone_backend/) \- Run a backend-specific command.

* # [rclone bisync](https://rclone.org/commands/rclone_bisync/) \- Perform bidirectional synchronization between two paths.

* # [rclone cat](https://rclone.org/commands/rclone_cat/) \- Concatenates any files and sends them to stdout.

* # [rclone check](https://rclone.org/commands/rclone_check/) \- Checks the files in the source and destination match.

* # [rclone checksum](https://rclone.org/commands/rclone_checksum/) \- Checks the files in the destination against a SUM file.

* # [rclone cleanup](https://rclone.org/commands/rclone_cleanup/) \- Clean up the remote if possible.

* # [rclone completion](https://rclone.org/commands/rclone_completion/) \- Output completion script for a given shell.

* # [rclone config](https://rclone.org/commands/rclone_config/) \- Enter an interactive configuration session.

* # [rclone convmv](https://rclone.org/commands/rclone_convmv/) \- Convert file and directory names in place.

* # [rclone copy](https://rclone.org/commands/rclone_copy/) \- Copy files from source to dest, skipping identical files.

* # [rclone copyto](https://rclone.org/commands/rclone_copyto/) \- Copy files from source to dest, skipping identical files.

* # [rclone copyurl](https://rclone.org/commands/rclone_copyurl/) \- Copy the contents of the URL supplied content to dest:path.

* # [rclone cryptcheck](https://rclone.org/commands/rclone_cryptcheck/) \- Cryptcheck checks the integrity of an encrypted remote.

* # [rclone cryptdecode](https://rclone.org/commands/rclone_cryptdecode/) \- Cryptdecode returns unencrypted file names.

* # [rclone dedupe](https://rclone.org/commands/rclone_dedupe/) \- Interactively find duplicate filenames and delete/rename them.

* # [rclone delete](https://rclone.org/commands/rclone_delete/) \- Remove the files in path.

* # [rclone deletefile](https://rclone.org/commands/rclone_deletefile/) \- Remove a single file from remote.

* # [rclone gendocs](https://rclone.org/commands/rclone_gendocs/) \- Output markdown docs for rclone to the directory supplied.

* # [rclone gitannex](https://rclone.org/commands/rclone_gitannex/) \- Speaks with git-annex over stdin/stdout.

* # [rclone hashsum](https://rclone.org/commands/rclone_hashsum/) \- Produces a hashsum file for all the objects in the path.

* # [rclone link](https://rclone.org/commands/rclone_link/) \- Generate public link to file/folder.

* # [rclone listremotes](https://rclone.org/commands/rclone_listremotes/) \- List all the remotes in the config file and defined in environment variables.

* # [rclone ls](https://rclone.org/commands/rclone_ls/) \- List the objects in the path with size and path.

* # [rclone lsd](https://rclone.org/commands/rclone_lsd/) \- List all directories/containers/buckets in the path.

* # [rclone lsf](https://rclone.org/commands/rclone_lsf/) \- List directories and objects in remote:path formatted for parsing.

* # [rclone lsjson](https://rclone.org/commands/rclone_lsjson/) \- List directories and objects in the path in JSON format.

* # [rclone lsl](https://rclone.org/commands/rclone_lsl/) \- List the objects in path with modification time, size and path.

* # [rclone md5sum](https://rclone.org/commands/rclone_md5sum/) \- Produces an md5sum file for all the objects in the path.

* # [rclone mkdir](https://rclone.org/commands/rclone_mkdir/) \- Make the path if it doesn't already exist.

* # [rclone mount](https://rclone.org/commands/rclone_mount/) \- Mount the remote as file system on a mountpoint.

* # [rclone move](https://rclone.org/commands/rclone_move/) \- Move files from source to dest.

* # [rclone moveto](https://rclone.org/commands/rclone_moveto/) \- Move file or directory from source to dest.

* # [rclone ncdu](https://rclone.org/commands/rclone_ncdu/) \- Explore a remote with a text based user interface.

* # [rclone nfsmount](https://rclone.org/commands/rclone_nfsmount/) \- Mount the remote as file system on a mountpoint.

* # [rclone obscure](https://rclone.org/commands/rclone_obscure/) \- Obscure password for use in the rclone config file.

* # [rclone purge](https://rclone.org/commands/rclone_purge/) \- Remove the path and all of its contents.

* # [rclone rc](https://rclone.org/commands/rclone_rc/) \- Run a command against a running rclone.

* # [rclone rcat](https://rclone.org/commands/rclone_rcat/) \- Copies standard input to file on remote.

* # [rclone rcd](https://rclone.org/commands/rclone_rcd/) \- Run rclone listening to remote control commands only.

* # [rclone rmdir](https://rclone.org/commands/rclone_rmdir/) \- Remove the empty directory at path.

* # [rclone rmdirs](https://rclone.org/commands/rclone_rmdirs/) \- Remove empty directories under the path.

* # [rclone selfupdate](https://rclone.org/commands/rclone_selfupdate/) \- Update the rclone binary.

* # [rclone serve](https://rclone.org/commands/rclone_serve/) \- Serve a remote over a protocol.

* # [rclone settier](https://rclone.org/commands/rclone_settier/) \- Changes storage class/tier of objects in remote.

* # [rclone sha1sum](https://rclone.org/commands/rclone_sha1sum/) \- Produces an sha1sum file for all the objects in the path.

* # [rclone size](https://rclone.org/commands/rclone_size/) \- Prints the total size and number of objects in remote:path.

* # [rclone sync](https://rclone.org/commands/rclone_sync/) \- Make source and dest identical, modifying destination only.

* # [rclone test](https://rclone.org/commands/rclone_test/) \- Run a test command

* # [rclone touch](https://rclone.org/commands/rclone_touch/) \- Create new file or change file modification time.

* # [rclone tree](https://rclone.org/commands/rclone_tree/) \- List the contents of the remote in a tree like fashion.

* # [rclone version](https://rclone.org/commands/rclone_version/) \- Show the version number.

# 

# 

# 

# 

# 

# 

# 

# 

# 

# 

# 

# 

# rclone check

Checks the files in the source and destination match.

## Synopsis

Checks the files in the source and destination match. It compares sizes and hashes (MD5 or SHA1) and logs a report of files that don't match. It doesn't alter the source or destination.

For the [crypt](https://rclone.org/crypt/) remote there is a dedicated command, [cryptcheck](https://rclone.org/commands/rclone_cryptcheck/), that are able to check the checksums of the encrypted files.

If you supply the \--size-only flag, it will only compare the sizes not the hashes as well. Use this for a quick check.

If you supply the \--download flag, it will download the data from both remotes and check them against each other on the fly. This can be useful for remotes that don't support hashes or if you really want to check all the data.

If you supply the \--checkfile HASH flag with a valid hash name, the source:path must point to a text file in the SUM format.

If you supply the \--one-way flag, it will only check that files in the source match the files in the destination, not the other way around. This means that extra files in the destination that are not in the source will not be detected.

The \--differ, \--missing-on-dst, \--missing-on-src, \--match and \--error flags write paths, one per line, to the file name (or stdout if it is \-) supplied. What they write is described in the help below. For example \--differ will write all paths which are present on both the source and destination but different.

The \--combined flag will write a file (or stdout) which contains all file paths with a symbol and then a space and then the path to tell you what happened to it. These are reminiscent of diff files.

* \= path means path was found in source and destination and was identical  
* \- path means path was missing on the source, so only in the destination  
* \+ path means path was missing on the destination, so only in the source  
* \* path means path was present in source and destination but different.  
* \! path means there was an error reading or hashing the source or dest.

The default number of parallel checks is 8\. See the [\--checkers](https://rclone.org/docs/#checkers-int) option for more information.

rclone check source:path dest:path \[flags\]

## Options

 \-C, \--checkfile string        Treat source:path as a SUM file with hashes of given type  
      \--combined string         Make a combined report of changes to this file  
      \--differ string           Report all non-matching files to this file  
      \--download                Check by downloading rather than with hash  
      \--error string            Report all files with errors (hashing or reading) to this file  
  \-h, \--help                    help for check  
      \--match string            Report all matching files to this file  
      \--missing-on-dst string   Report all files missing from the destination to this file  
      \--missing-on-src string   Report all files missing from the source to this file  
      \--one-way                 Check one way only, source files must exist on remote

Options shared with other commands are described next. See the [global flags page](https://rclone.org/flags/) for global options not listed here.

### **Check Options**

Flags used for check commands

     \--max-backlog int   Maximum number of objects in sync or check backlog (default 10000\)

### **Filter Options**

Flags for filtering directory listings

     \--delete-excluded                     Delete files on dest excluded from sync

     \--exclude stringArray                 Exclude files matching pattern

     \--exclude-from stringArray            Read file exclude patterns from file (use \- to read from stdin)

     \--exclude-if-present stringArray      Exclude directories if filename is present

     \--files-from stringArray              Read list of source-file names from file (use \- to read from stdin)

     \--files-from-raw stringArray          Read list of source-file names from file without any processing of lines (use \- to read from stdin)

 \-f, \--filter stringArray                  Add a file filtering rule

     \--filter-from stringArray             Read file filtering patterns from a file (use \- to read from stdin)

     \--hash-filter string                  Partition filenames by hash k/n or randomly @/n

     \--ignore-case                         Ignore case in filters (case insensitive)

     \--include stringArray                 Include files matching pattern

     \--include-from stringArray            Read file include patterns from file (use \- to read from stdin)

     \--max-age Duration                    Only transfer files younger than this in s or suffix ms|s|m|h|d|w|M|y (default off)

     \--max-depth int                       If set limits the recursion depth to this (default \-1)

     \--max-size SizeSuffix                 Only transfer files smaller than this in KiB or suffix B|K|M|G|T|P (default off)

     \--metadata-exclude stringArray        Exclude metadatas matching pattern

     \--metadata-exclude-from stringArray   Read metadata exclude patterns from file (use \- to read from stdin)

     \--metadata-filter stringArray         Add a metadata filtering rule

     \--metadata-filter-from stringArray    Read metadata filtering patterns from a file (use \- to read from stdin)

     \--metadata-include stringArray        Include metadatas matching pattern

     \--metadata-include-from stringArray   Read metadata include patterns from file (use \- to read from stdin)

     \--min-age Duration                    Only transfer files older than this in s or suffix ms|s|m|h|d|w|M|y (default off)

     \--min-size SizeSuffix                 Only transfer files bigger than this in KiB or suffix B|K|M|G|T|P (default off)

### **Listing Options**

Flags for listing directories

     \--default-time Time   Time to show if modtime is unknown for files and directories (default 2000-01-01T00:00:00Z)

     \--fast-list           Use recursive list if available; uses more memory but fewer transactions

# rclone lsjson

List directories and objects in the path in JSON format.

## Synopsis

List directories and objects in the path in JSON format.

The output is an array of Items, where each Item looks like this:

{

 "Hashes" : {

   "SHA-1" : "f572d396fae9206628714fb2ce00f72e94f2258f",

   "MD5" : "b1946ac92492d2347c6235b4d2611184",

   "DropboxHash" : "ecb65bb98f9d905b70458986c39fcbad7715e5f2fcc3b1f07767d7c83e2438cc"

 },

 "ID": "y2djkhiujf83u33",

 "OrigID": "UYOJVTUW00Q1RzTDA",

 "IsBucket" : false,

 "IsDir" : false,

 "MimeType" : "application/octet-stream",

 "ModTime" : "2017-05-31T16:15:57.034468261+01:00",

 "Name" : "file.txt",

 "Encrypted" : "v0qpsdq8anpci8n929v3uu9338",

 "EncryptedPath" : "kja9098349023498/v0qpsdq8anpci8n929v3uu9338",

 "Path" : "full/path/goes/here/file.txt",

 "Size" : 6,

 "Tier" : "hot",

}

The exact set of properties included depends on the backend:

* The property IsBucket will only be included for bucket-based remotes, and only for directories that are buckets. It will always be omitted when value is not true.  
* Properties Encrypted and EncryptedPath will only be included for encrypted remotes, and (as mentioned below) only if the \--encrypted option is set.

Different options may also affect which properties are included:

* If \--hash is not specified, the Hashes property will be omitted. The types of hash can be specified with the \--hash-type parameter (which may be repeated). If \--hash-type is set then it implies \--hash.  
* If \--no-modtime is specified then ModTime will be blank. This can speed things up on remotes where reading the ModTime takes an extra request (e.g. s3, swift).  
* If \--no-mimetype is specified then MimeType will be blank. This can speed things up on remotes where reading the MimeType takes an extra request (e.g. s3, swift).  
* If \--encrypted is not specified the Encrypted and EncryptedPath properties will be omitted \- even for encrypted remotes.  
* If \--metadata is set then an additional Metadata property will be returned. This will have [metadata](https://rclone.org/docs/#metadata) in rclone standard format as a JSON object.

The default is to list directories and files/objects, but this can be changed with the following options:

* If \--dirs-only is specified then directories will be returned only, no files/objects.  
* If \--files-only is specified then files will be returned only, no directories.

If \--stat is set then the output is not an array of items, but instead a single JSON blob will be returned about the item pointed to. This will return an error if the item isn't found, however on bucket based backends (like s3, gcs, b2, azureblob etc) if the item isn't found it will return an empty directory, as it isn't possible to tell empty directories from missing directories there.

The Path field will only show folders below the remote path being listed. If "remote:path" contains the file "subfolder/file.txt", the Path for "file.txt" will be "subfolder/file.txt", not "remote:path/subfolder/file.txt". When used without \--recursive the Path will always be the same as Name.

The time is in RFC3339 format with up to nanosecond precision. The number of decimal digits in the seconds will depend on the precision that the remote can hold the times, so if times are accurate to the nearest millisecond (e.g. Google Drive) then 3 digits will always be shown ("2017-05-31T16:15:57.034+01:00") whereas if the times are accurate to the nearest second (Dropbox, Box, WebDav, etc.) no digits will be shown ("2017-05-31T16:15:57+01:00").

The whole output can be processed as a JSON blob, or alternatively it can be processed line by line as each item is written on individual lines (except with \--stat).

Any of the filtering options can be applied to this command.

There are several related list commands

* ls to list size and path of objects only  
* lsl to list modification time, size and path of objects only  
* lsd to list directories only  
* lsf to list objects and directories in easy to parse format  
* lsjson to list objects and directories in JSON format

ls,lsl,lsd are designed to be human-readable. lsf is designed to be human and machine-readable. lsjson is designed to be machine-readable.

Note that ls and lsl recurse by default \- use \--max-depth 1 to stop the recursion.

The other list commands lsd,lsf,lsjson do not recurse by default \- use \-R to make them recurse.

List commands prefer a recursive method that uses more memory but fewer transactions by default. Use \--disable ListR to suppress the behavior. See [\--fast-list](https://rclone.org/docs/#fast-list) for more details.

Listing a nonexistent directory will produce an error except for remotes which can't have empty directories (e.g. s3, swift, or gcs \- the bucket-based remotes).

rclone lsjson remote:path \[flags\]

## Options

     \--dirs-only               Show only directories in the listing  
      \--encrypted               Show the encrypted names  
      \--files-only              Show only files in the listing  
      \--hash                    Include hashes in the output (may take longer)  
      \--hash-type stringArray   Show only this hash type (may be repeated)  
  \-h, \--help                    help for lsjson  
  \-M, \--metadata                Add metadata to the listing  
      \--no-mimetype             Don't read the mime type (can speed things up)  
      \--no-modtime              Don't read the modification time (can speed things up)  
      \--original                Show the ID of the underlying Object  
  \-R, \--recursive               Recurse into the listing  
      \--stat                    Just return the info for the pointed to file

Options shared with other commands are described next. See the [global flags page](https://rclone.org/flags/) for global options not listed here.

### **Filter Options**

Flags for filtering directory listings

     \--delete-excluded                     Delete files on dest excluded from sync

     \--exclude stringArray                 Exclude files matching pattern

     \--exclude-from stringArray            Read file exclude patterns from file (use \- to read from stdin)

     \--exclude-if-present stringArray      Exclude directories if filename is present

     \--files-from stringArray              Read list of source-file names from file (use \- to read from stdin)

     \--files-from-raw stringArray          Read list of source-file names from file without any processing of lines (use \- to read from stdin)

 \-f, \--filter stringArray                  Add a file filtering rule

     \--filter-from stringArray             Read file filtering patterns from a file (use \- to read from stdin)

     \--hash-filter string                  Partition filenames by hash k/n or randomly @/n

     \--ignore-case                         Ignore case in filters (case insensitive)

     \--include stringArray                 Include files matching pattern

     \--include-from stringArray            Read file include patterns from file (use \- to read from stdin)

     \--max-age Duration                    Only transfer files younger than this in s or suffix ms|s|m|h|d|w|M|y (default off)

     \--max-depth int                       If set limits the recursion depth to this (default \-1)

     \--max-size SizeSuffix                 Only transfer files smaller than this in KiB or suffix B|K|M|G|T|P (default off)

     \--metadata-exclude stringArray        Exclude metadatas matching pattern

     \--metadata-exclude-from stringArray   Read metadata exclude patterns from file (use \- to read from stdin)

     \--metadata-filter stringArray         Add a metadata filtering rule

     \--metadata-filter-from stringArray    Read metadata filtering patterns from a file (use \- to read from stdin)

     \--metadata-include stringArray        Include metadatas matching pattern

     \--metadata-include-from stringArray   Read metadata include patterns from file (use \- to read from stdin)

     \--min-age Duration                    Only transfer files older than this in s or suffix ms|s|m|h|d|w|M|y (default off)

     \--min-size SizeSuffix                 Only transfer files bigger than this in KiB or suffix B|K|M|G|T|P (default off)

### **Listing Options**

Flags for listing directories

     \--default-time Time   Time to show if modtime is unknown for files and directories (default 2000-01-01T00:00:00Z)

     \--fast-list           Use recursive list if available; uses more memory but fewer transactions

# rclone sync

Make source and dest identical, modifying destination only.

## Synopsis

Sync the source to the destination, changing the destination only. Doesn't transfer files that are identical on source and destination, testing by size and modification time or MD5SUM. Destination is updated to match source, including deleting files if necessary (except duplicate objects, see below). If you don't want to delete files from destination, use the [copy](https://rclone.org/commands/rclone_copy/) command instead.

Important: Since this can cause data loss, test first with the \--dry-run or the \--interactive/i flag.

rclone sync \--interactive SOURCE remote:DESTINATION

Files in the destination won't be deleted if there were any errors at any point. Duplicate objects (files with the same name, on those providers that support it) are not yet handled. Files that are excluded won't be deleted unless \--delete-excluded is used. Symlinks won't be transferred or deleted from local file systems unless \--links is used.

It is always the contents of the directory that is synced, not the directory itself. So when source:path is a directory, it's the contents of source:path that are copied, not the directory name and contents. See extended explanation in the [copy](https://rclone.org/commands/rclone_copy/) command if unsure.

If dest:path doesn't exist, it is created and the source:path contents go there.

It is not possible to sync overlapping remotes. However, you may exclude the destination from the sync with a filter rule or by putting an exclude-if-present file inside the destination directory and sync to a destination that is inside the source directory.

Rclone will sync the modification times of files and directories if the backend supports it. If metadata syncing is required then use the \--metadata flag.

Note that the modification time and metadata for the root directory will not be synced. See [https://github.com/rclone/rclone/issues/7652](https://github.com/rclone/rclone/issues/7652) for more info.

Note: Use the \-P/\--progress flag to view real-time transfer statistics

Note: Use the rclone dedupe command to deal with "Duplicate object/directory found in source/destination \- ignoring" errors. See [this forum post](https://forum.rclone.org/t/sync-not-clearing-duplicates/14372) for more info.

## Logger Flags

The \--differ, \--missing-on-dst, \--missing-on-src, \--match and \--error flags write paths, one per line, to the file name (or stdout if it is \-) supplied. What they write is described in the help below. For example \--differ will write all paths which are present on both the source and destination but different.

The \--combined flag will write a file (or stdout) which contains all file paths with a symbol and then a space and then the path to tell you what happened to it. These are reminiscent of diff files.

* \= path means path was found in source and destination and was identical  
* \- path means path was missing on the source, so only in the destination  
* \+ path means path was missing on the destination, so only in the source  
* \* path means path was present in source and destination but different.  
* \! path means there was an error reading or hashing the source or dest.

The \--dest-after flag writes a list file using the same format flags as [lsf](https://rclone.org/commands/rclone_lsf/#synopsis) (including [customizable options for hash, modtime, etc.](https://rclone.org/commands/rclone_lsf/#synopsis)) Conceptually it is similar to rsync's \--itemize-changes, but not identical \-- it should output an accurate list of what will be on the destination after the command is finished.

When the \--no-traverse flag is set, all logs involving files that exist only on the destination will be incomplete or completely missing.

Note that these logger flags have a few limitations, and certain scenarios are not currently supported:

* \--max-duration / CutoffModeHard  
* \--compare-dest / \--copy-dest  
* server-side moves of an entire dir at once  
* High-level retries, because there would be duplicates (use \--retries 1 to disable)  
* Possibly some unusual error scenarios

Note also that each file is logged during execution, as opposed to after, so it is most useful as a predictor of what SHOULD happen to each file (which may or may not match what actually DID).

rclone sync source:path dest:path \[flags\]

## Options

     \--absolute                Put a leading / in front of path names  
      \--combined string         Make a combined report of changes to this file  
      \--create-empty-src-dirs   Create empty source dirs on destination after sync  
      \--csv                     Output in CSV format  
      \--dest-after string       Report all files that exist on the dest post-sync  
      \--differ string           Report all non-matching files to this file  
  \-d, \--dir-slash               Append a slash to directory names (default true)  
      \--dirs-only               Only list directories  
      \--error string            Report all files with errors (hashing or reading) to this file  
      \--files-only              Only list files (default true)  
  \-F, \--format string           Output format \- see lsf help for details (default "p")  
      \--hash h                  Use this hash when h is used in the format MD5|SHA-1|DropboxHash (default "md5")  
  \-h, \--help                    help for sync  
      \--match string            Report all matching files to this file  
      \--missing-on-dst string   Report all files missing from the destination to this file  
      \--missing-on-src string   Report all files missing from the source to this file  
  \-s, \--separator string        Separator for the items in the format (default ";")  
  \-t, \--timeformat string       Specify a custom time format \- see docs for details (default: 2006-01-02 15:04:05)

Options shared with other commands are described next. See the [global flags page](https://rclone.org/flags/) for global options not listed here.

### **Copy Options**

Flags for anything which can copy a file

     \--check-first                                 Do all the checks before starting transfers

 \-c, \--checksum                                    Check for changes with size & checksum (if available, or fallback to size only)

     \--compare-dest stringArray                    Include additional server-side paths during comparison

     \--copy-dest stringArray                       Implies \--compare-dest but also copies files from paths into destination

     \--cutoff-mode HARD|SOFT|CAUTIOUS              Mode to stop transfers when reaching the max transfer limit HARD|SOFT|CAUTIOUS (default HARD)

     \--ignore-case-sync                            Ignore case when synchronizing

     \--ignore-checksum                             Skip post copy check of checksums

     \--ignore-existing                             Skip all files that exist on destination

     \--ignore-size                                 Ignore size when skipping use modtime or checksum

 \-I, \--ignore-times                                Don't skip items that match size and time \- transfer all unconditionally

     \--immutable                                   Do not modify files, fail if existing files have been modified

     \--inplace                                     Download directly to destination file instead of atomic download to temp/rename

 \-l, \--links                                       Translate symlinks to/from regular files with a '.rclonelink' extension

     \--max-backlog int                             Maximum number of objects in sync or check backlog (default 10000\)

     \--max-duration Duration                       Maximum duration rclone will transfer data for (default 0s)

     \--max-transfer SizeSuffix                     Maximum size of data to transfer (default off)

 \-M, \--metadata                                    If set, preserve metadata when copying objects

     \--modify-window Duration                      Max time diff to be considered the same (default 1ns)

     \--multi-thread-chunk-size SizeSuffix          Chunk size for multi-thread downloads / uploads, if not set by filesystem (default 64Mi)

     \--multi-thread-cutoff SizeSuffix              Use multi-thread downloads for files above this size (default 256Mi)

     \--multi-thread-streams int                    Number of streams to use for multi-thread downloads (default 4\)

     \--multi-thread-write-buffer-size SizeSuffix   In memory buffer size for writing when in multi-thread mode (default 128Ki)

     \--name-transform stringArray                  Transform paths during the copy process

     \--no-check-dest                               Don't check the destination, copy regardless

     \--no-traverse                                 Don't traverse destination file system on copy

     \--no-update-dir-modtime                       Don't update directory modification times

     \--no-update-modtime                           Don't update destination modtime if files identical

     \--order-by string                             Instructions on how to order the transfers, e.g. 'size,descending'

     \--partial-suffix string                       Add partial-suffix to temporary file name when \--inplace is not used (default ".partial")

     \--refresh-times                               Refresh the modtime of remote files

     \--server-side-across-configs                  Allow server-side operations (e.g. copy) to work across different configs

     \--size-only                                   Skip based on size only, not modtime or checksum

     \--streaming-upload-cutoff SizeSuffix          Cutoff for switching to chunked upload if file size is unknown, upload starts after reaching cutoff or when file ends (default 100Ki)

 \-u, \--update                                      Skip files that are newer on the destination

### **Sync Options**

Flags used for sync commands

     \--backup-dir string               Make backups into hierarchy based in DIR

     \--delete-after                    When synchronizing, delete files on destination after transferring (default)

     \--delete-before                   When synchronizing, delete files on destination before transferring

     \--delete-during                   When synchronizing, delete files during transfer

     \--fix-case                        Force rename of case insensitive dest to match source

     \--ignore-errors                   Delete even if there are I/O errors

     \--list-cutoff int                 To save memory, sort directory listings on disk above this threshold (default 1000000\)

     \--max-delete int                  When synchronizing, limit the number of deletes (default \-1)

     \--max-delete-size SizeSuffix      When synchronizing, limit the total size of deletes (default off)

     \--suffix string                   Suffix to add to changed files

     \--suffix-keep-extension           Preserve the extension when using \--suffix

     \--track-renames                   When synchronizing, track file renames and do a server-side move if possible

     \--track-renames-strategy string   Strategies to use when synchronizing using track-renames hash|modtime|leaf (default "hash")

### **Important Options**

Important flags useful for most commands

 \-n, \--dry-run         Do a trial run with no permanent changes

 \-i, \--interactive     Enable interactive mode

 \-v, \--verbose count   Print lots more stuff (repeat for more)

### **Filter Options**

Flags for filtering directory listings

     \--delete-excluded                     Delete files on dest excluded from sync

     \--exclude stringArray                 Exclude files matching pattern

     \--exclude-from stringArray            Read file exclude patterns from file (use \- to read from stdin)

     \--exclude-if-present stringArray      Exclude directories if filename is present

     \--files-from stringArray              Read list of source-file names from file (use \- to read from stdin)

     \--files-from-raw stringArray          Read list of source-file names from file without any processing of lines (use \- to read from stdin)

 \-f, \--filter stringArray                  Add a file filtering rule

     \--filter-from stringArray             Read file filtering patterns from a file (use \- to read from stdin)

     \--hash-filter string                  Partition filenames by hash k/n or randomly @/n

     \--ignore-case                         Ignore case in filters (case insensitive)

     \--include stringArray                 Include files matching pattern

     \--include-from stringArray            Read file include patterns from file (use \- to read from stdin)

     \--max-age Duration                    Only transfer files younger than this in s or suffix ms|s|m|h|d|w|M|y (default off)

     \--max-depth int                       If set limits the recursion depth to this (default \-1)

     \--max-size SizeSuffix                 Only transfer files smaller than this in KiB or suffix B|K|M|G|T|P (default off)

     \--metadata-exclude stringArray        Exclude metadatas matching pattern

     \--metadata-exclude-from stringArray   Read metadata exclude patterns from file (use \- to read from stdin)

     \--metadata-filter stringArray         Add a metadata filtering rule

     \--metadata-filter-from stringArray    Read metadata filtering patterns from a file (use \- to read from stdin)

     \--metadata-include stringArray        Include metadatas matching pattern

     \--metadata-include-from stringArray   Read metadata include patterns from file (use \- to read from stdin)

     \--min-age Duration                    Only transfer files older than this in s or suffix ms|s|m|h|d|w|M|y (default off)

     \--min-size SizeSuffix                 Only transfer files bigger than this in KiB or suffix B|K|M|G|T|P (default off)

### **Listing Options**

Flags for listing directories

     \--default-time Time   Time to show if modtime is unknown for files and directories (default 2000-01-01T00:00:00Z)

     \--fast-list           Use recursive list if available; uses more memory but fewer transactions

## See Also

* [rclone](https://rclone.org/commands/rclone/) \- Show help for rclone commands, flags and backends.

# rclone copy

Copy files from source to dest, skipping identical files.

## Synopsis

Copy the source to the destination. Does not transfer files that are identical on source and destination, testing by size and modification time or MD5SUM. Doesn't delete files from the destination. If you want to also delete files from destination, to make it match source, use the [sync](https://rclone.org/commands/rclone_sync/) command instead.

Note that it is always the contents of the directory that is synced, not the directory itself. So when source:path is a directory, it's the contents of source:path that are copied, not the directory name and contents.

To copy single files, use the [copyto](https://rclone.org/commands/rclone_copyto/) command instead.

If dest:path doesn't exist, it is created and the source:path contents go there.

For example

rclone copy source:sourcepath dest:destpath

Let's say there are two files in sourcepath

sourcepath/one.txt

sourcepath/two.txt

This copies them to

destpath/one.txt

destpath/two.txt

Not to

destpath/sourcepath/one.txt

destpath/sourcepath/two.txt

If you are familiar with rsync, rclone always works as if you had written a trailing / \- meaning "copy the contents of this directory". This applies to all commands and whether you are talking about the source or destination.

See the [\--no-traverse](https://rclone.org/docs/#no-traverse) option for controlling whether rclone lists the destination directory or not. Supplying this option when copying a small number of files into a large destination can speed transfers up greatly.

For example, if you have many files in /path/to/src but only a few of them change every day, you can copy all the files which have changed recently very efficiently like this:

rclone copy \--max-age 24h \--no-traverse /path/to/src remote:

Rclone will sync the modification times of files and directories if the backend supports it. If metadata syncing is required then use the \--metadata flag.

Note that the modification time and metadata for the root directory will not be synced. See [issue \#7652](https://github.com/rclone/rclone/issues/7652) for more info.

Note: Use the \-P/\--progress flag to view real-time transfer statistics.

Note: Use the \--dry-run or the \--interactive/\-i flag to test without copying anything.

## Logger Flags

The \--differ, \--missing-on-dst, \--missing-on-src, \--match and \--error flags write paths, one per line, to the file name (or stdout if it is \-) supplied. What they write is described in the help below. For example \--differ will write all paths which are present on both the source and destination but different.

The \--combined flag will write a file (or stdout) which contains all file paths with a symbol and then a space and then the path to tell you what happened to it. These are reminiscent of diff files.

* \= path means path was found in source and destination and was identical  
* \- path means path was missing on the source, so only in the destination  
* \+ path means path was missing on the destination, so only in the source  
* \* path means path was present in source and destination but different.  
* \! path means there was an error reading or hashing the source or dest.

The \--dest-after flag writes a list file using the same format flags as [lsf](https://rclone.org/commands/rclone_lsf/#synopsis) (including [customizable options for hash, modtime, etc.](https://rclone.org/commands/rclone_lsf/#synopsis)) Conceptually it is similar to rsync's \--itemize-changes, but not identical \-- it should output an accurate list of what will be on the destination after the command is finished.

When the \--no-traverse flag is set, all logs involving files that exist only on the destination will be incomplete or completely missing.

Note that these logger flags have a few limitations, and certain scenarios are not currently supported:

* \--max-duration / CutoffModeHard  
* \--compare-dest / \--copy-dest  
* server-side moves of an entire dir at once  
* High-level retries, because there would be duplicates (use \--retries 1 to disable)  
* Possibly some unusual error scenarios

Note also that each file is logged during execution, as opposed to after, so it is most useful as a predictor of what SHOULD happen to each file (which may or may not match what actually DID).

rclone copy source:path dest:path \[flags\]

## Options

     \--absolute                Put a leading / in front of path names  
      \--combined string         Make a combined report of changes to this file  
      \--create-empty-src-dirs   Create empty source dirs on destination after copy  
      \--csv                     Output in CSV format  
      \--dest-after string       Report all files that exist on the dest post-sync  
      \--differ string           Report all non-matching files to this file  
  \-d, \--dir-slash               Append a slash to directory names (default true)  
      \--dirs-only               Only list directories  
      \--error string            Report all files with errors (hashing or reading) to this file  
      \--files-only              Only list files (default true)  
  \-F, \--format string           Output format \- see lsf help for details (default "p")  
      \--hash h                  Use this hash when h is used in the format MD5|SHA-1|DropboxHash (default "md5")  
  \-h, \--help                    help for copy  
      \--match string            Report all matching files to this file  
      \--missing-on-dst string   Report all files missing from the destination to this file  
      \--missing-on-src string   Report all files missing from the source to this file  
  \-s, \--separator string        Separator for the items in the format (default ";")  
  \-t, \--timeformat string       Specify a custom time format \- see docs for details (default: 2006-01-02 15:04:05)

Options shared with other commands are described next. See the [global flags page](https://rclone.org/flags/) for global options not listed here.

### **Copy Options**

Flags for anything which can copy a file

     \--check-first                                 Do all the checks before starting transfers

 \-c, \--checksum                                    Check for changes with size & checksum (if available, or fallback to size only)

     \--compare-dest stringArray                    Include additional server-side paths during comparison

     \--copy-dest stringArray                       Implies \--compare-dest but also copies files from paths into destination

     \--cutoff-mode HARD|SOFT|CAUTIOUS              Mode to stop transfers when reaching the max transfer limit HARD|SOFT|CAUTIOUS (default HARD)

     \--ignore-case-sync                            Ignore case when synchronizing

     \--ignore-checksum                             Skip post copy check of checksums

     \--ignore-existing                             Skip all files that exist on destination

     \--ignore-size                                 Ignore size when skipping use modtime or checksum

 \-I, \--ignore-times                                Don't skip items that match size and time \- transfer all unconditionally

     \--immutable                                   Do not modify files, fail if existing files have been modified

     \--inplace                                     Download directly to destination file instead of atomic download to temp/rename

 \-l, \--links                                       Translate symlinks to/from regular files with a '.rclonelink' extension

     \--max-backlog int                             Maximum number of objects in sync or check backlog (default 10000\)

     \--max-duration Duration                       Maximum duration rclone will transfer data for (default 0s)

     \--max-transfer SizeSuffix                     Maximum size of data to transfer (default off)

 \-M, \--metadata                                    If set, preserve metadata when copying objects

     \--modify-window Duration                      Max time diff to be considered the same (default 1ns)

     \--multi-thread-chunk-size SizeSuffix          Chunk size for multi-thread downloads / uploads, if not set by filesystem (default 64Mi)

     \--multi-thread-cutoff SizeSuffix              Use multi-thread downloads for files above this size (default 256Mi)

     \--multi-thread-streams int                    Number of streams to use for multi-thread downloads (default 4\)

     \--multi-thread-write-buffer-size SizeSuffix   In memory buffer size for writing when in multi-thread mode (default 128Ki)

     \--name-transform stringArray                  Transform paths during the copy process

     \--no-check-dest                               Don't check the destination, copy regardless

     \--no-traverse                                 Don't traverse destination file system on copy

     \--no-update-dir-modtime                       Don't update directory modification times

     \--no-update-modtime                           Don't update destination modtime if files identical

     \--order-by string                             Instructions on how to order the transfers, e.g. 'size,descending'

     \--partial-suffix string                       Add partial-suffix to temporary file name when \--inplace is not used (default ".partial")

     \--refresh-times                               Refresh the modtime of remote files

     \--server-side-across-configs                  Allow server-side operations (e.g. copy) to work across different configs

     \--size-only                                   Skip based on size only, not modtime or checksum

     \--streaming-upload-cutoff SizeSuffix          Cutoff for switching to chunked upload if file size is unknown, upload starts after reaching cutoff or when file ends (default 100Ki)

 \-u, \--update                                      Skip files that are newer on the destination

### **Important Options**

Important flags useful for most commands

 \-n, \--dry-run         Do a trial run with no permanent changes

 \-i, \--interactive     Enable interactive mode

 \-v, \--verbose count   Print lots more stuff (repeat for more)

### **Filter Options**

Flags for filtering directory listings

     \--delete-excluded                     Delete files on dest excluded from sync

     \--exclude stringArray                 Exclude files matching pattern

     \--exclude-from stringArray            Read file exclude patterns from file (use \- to read from stdin)

     \--exclude-if-present stringArray      Exclude directories if filename is present

     \--files-from stringArray              Read list of source-file names from file (use \- to read from stdin)

     \--files-from-raw stringArray          Read list of source-file names from file without any processing of lines (use \- to read from stdin)

 \-f, \--filter stringArray                  Add a file filtering rule

     \--filter-from stringArray             Read file filtering patterns from a file (use \- to read from stdin)

     \--hash-filter string                  Partition filenames by hash k/n or randomly @/n

     \--ignore-case                         Ignore case in filters (case insensitive)

     \--include stringArray                 Include files matching pattern

     \--include-from stringArray            Read file include patterns from file (use \- to read from stdin)

     \--max-age Duration                    Only transfer files younger than this in s or suffix ms|s|m|h|d|w|M|y (default off)

     \--max-depth int                       If set limits the recursion depth to this (default \-1)

     \--max-size SizeSuffix                 Only transfer files smaller than this in KiB or suffix B|K|M|G|T|P (default off)

     \--metadata-exclude stringArray        Exclude metadatas matching pattern

     \--metadata-exclude-from stringArray   Read metadata exclude patterns from file (use \- to read from stdin)

     \--metadata-filter stringArray         Add a metadata filtering rule

     \--metadata-filter-from stringArray    Read metadata filtering patterns from a file (use \- to read from stdin)

     \--metadata-include stringArray        Include metadatas matching pattern

     \--metadata-include-from stringArray   Read metadata include patterns from file (use \- to read from stdin)

     \--min-age Duration                    Only transfer files older than this in s or suffix ms|s|m|h|d|w|M|y (default off)

     \--min-size SizeSuffix                 Only transfer files bigger than this in KiB or suffix B|K|M|G|T|P (default off)

### **Listing Options**

Flags for listing directories

     \--default-time Time   Time to show if modtime is unknown for files and directories (default 2000-01-01T00:00:00Z)

     \--fast-list           Use recursive list if available; uses more memory but fewer transactions

# rclone about

Get quota information from the remote.

## Synopsis

Prints quota information about a remote to standard output. The output is typically used, free, quota and trash contents.

E.g. Typical output from rclone about remote: is:

Total:   17 GiB

Used:    7.444 GiB

Free:    1.315 GiB

Trashed: 100.000 MiB

Other:   8.241 GiB

Where the fields are:

* Total: Total size available.  
* Used: Total size used.  
* Free: Total space available to this user.  
* Trashed: Total space used by trash.  
* Other: Total amount in other storage (e.g. Gmail, Google Photos).  
* Objects: Total number of objects in the storage.

All sizes are in number of bytes.

Applying a \--full flag to the command prints the bytes in full, e.g.

Total:   18253611008

Used:    7993453766

Free:    1411001220

Trashed: 104857602

Other:   8849156022

A \--json flag generates conveniently machine-readable output, e.g.

{

 "total": 18253611008,

 "used": 7993453766,

 "trashed": 104857602,

 "other": 8849156022,

 "free": 1411001220

}

Not all backends print all fields. Information is not included if it is not provided by a backend. Where the value is unlimited it is omitted.

Some backends does not support the rclone about command at all, see complete list in [documentation](https://rclone.org/overview/#optional-features).

rclone about remote: \[flags\]

## Options

     \--full   Full numbers instead of human-readable  
  \-h, \--help   help for about  
      \--json   Format output as JSON

See the [global flags page](https://rclone.org/flags/) for global options not listed here.

# Global Flags

This describes the global flags available to every rclone command split into groups.

## Copy

Flags for anything which can copy a file.

     \--check-first                                 Do all the checks before starting transfers  
  \-c, \--checksum                                    Check for changes with size & checksum (if available, or fallback to size only)  
      \--compare-dest stringArray                    Include additional server-side paths during comparison  
      \--copy-dest stringArray                       Implies \--compare-dest but also copies files from paths into destination  
      \--cutoff-mode HARD|SOFT|CAUTIOUS              Mode to stop transfers when reaching the max transfer limit HARD|SOFT|CAUTIOUS (default HARD)  
      \--ignore-case-sync                            Ignore case when synchronizing  
      \--ignore-checksum                             Skip post copy check of checksums  
      \--ignore-existing                             Skip all files that exist on destination  
      \--ignore-size                                 Ignore size when skipping use modtime or checksum  
  \-I, \--ignore-times                                Don't skip items that match size and time \- transfer all unconditionally  
      \--immutable                                   Do not modify files, fail if existing files have been modified  
      \--inplace                                     Download directly to destination file instead of atomic download to temp/rename  
  \-l, \--links                                       Translate symlinks to/from regular files with a '.rclonelink' extension  
      \--max-backlog int                             Maximum number of objects in sync or check backlog (default 10000\)  
      \--max-duration Duration                       Maximum duration rclone will transfer data for (default 0s)  
      \--max-transfer SizeSuffix                     Maximum size of data to transfer (default off)  
  \-M, \--metadata                                    If set, preserve metadata when copying objects  
      \--modify-window Duration                      Max time diff to be considered the same (default 1ns)  
      \--multi-thread-chunk-size SizeSuffix          Chunk size for multi-thread downloads / uploads, if not set by filesystem (default 64Mi)  
      \--multi-thread-cutoff SizeSuffix              Use multi-thread downloads for files above this size (default 256Mi)  
      \--multi-thread-streams int                    Number of streams to use for multi-thread downloads (default 4\)  
      \--multi-thread-write-buffer-size SizeSuffix   In memory buffer size for writing when in multi-thread mode (default 128Ki)  
      \--name-transform stringArray                  Transform paths during the copy process  
      \--no-check-dest                               Don't check the destination, copy regardless  
      \--no-traverse                                 Don't traverse destination file system on copy  
      \--no-update-dir-modtime                       Don't update directory modification times  
      \--no-update-modtime                           Don't update destination modtime if files identical  
      \--order-by string                             Instructions on how to order the transfers, e.g. 'size,descending'  
      \--partial-suffix string                       Add partial-suffix to temporary file name when \--inplace is not used (default ".partial")  
      \--refresh-times                               Refresh the modtime of remote files  
      \--server-side-across-configs                  Allow server-side operations (e.g. copy) to work across different configs  
      \--size-only                                   Skip based on size only, not modtime or checksum  
      \--streaming-upload-cutoff SizeSuffix          Cutoff for switching to chunked upload if file size is unknown, upload starts after reaching cutoff or when file ends (default 100Ki)  
  \-u, \--update                                      Skip files that are newer on the destination

## Sync

Flags used for sync commands.

     \--backup-dir string               Make backups into hierarchy based in DIR  
      \--delete-after                    When synchronizing, delete files on destination after transferring (default)  
      \--delete-before                   When synchronizing, delete files on destination before transferring  
      \--delete-during                   When synchronizing, delete files during transfer  
      \--fix-case                        Force rename of case insensitive dest to match source  
      \--ignore-errors                   Delete even if there are I/O errors  
      \--list-cutoff int                 To save memory, sort directory listings on disk above this threshold (default 1000000\)  
      \--max-delete int                  When synchronizing, limit the number of deletes (default \-1)  
      \--max-delete-size SizeSuffix      When synchronizing, limit the total size of deletes (default off)  
      \--suffix string                   Suffix to add to changed files  
      \--suffix-keep-extension           Preserve the extension when using \--suffix  
      \--track-renames                   When synchronizing, track file renames and do a server-side move if possible  
      \--track-renames-strategy string   Strategies to use when synchronizing using track-renames hash|modtime|leaf (default "hash")

## Important

Important flags useful for most commands.

 \-n, \--dry-run         Do a trial run with no permanent changes  
  \-i, \--interactive     Enable interactive mode  
  \-v, \--verbose count   Print lots more stuff (repeat for more)

## Check

Flags used for check commands.

     \--max-backlog int   Maximum number of objects in sync or check backlog (default 10000\)

## Networking

Flags for general networking and HTTP stuff.

     \--bind string                        Local address to bind to for outgoing connections, IPv4, IPv6 or name  
      \--bwlimit BwTimetable                Bandwidth limit in KiB/s, or use suffix B|K|M|G|T|P or a full timetable  
      \--bwlimit-file BwTimetable           Bandwidth limit per file in KiB/s, or use suffix B|K|M|G|T|P or a full timetable  
      \--ca-cert stringArray                CA certificate used to verify servers  
      \--client-cert string                 Client SSL certificate (PEM) for mutual TLS auth  
      \--client-key string                  Client SSL private key (PEM) for mutual TLS auth  
      \--client-pass string                 Password for client SSL private key (PEM) for mutual TLS auth (obscured) (obscured)  
      \--contimeout Duration                Connect timeout (default 1m0s)  
      \--disable-http-keep-alives           Disable HTTP keep-alives and use each connection once  
      \--disable-http2                      Disable HTTP/2 in the global transport  
      \--dscp string                        Set DSCP value to connections, value or name, e.g. CS1, LE, DF, AF21  
      \--expect-continue-timeout Duration   Timeout when using expect / 100-continue in HTTP (default 1s)  
      \--header stringArray                 Set HTTP header for all transactions  
      \--header-download stringArray        Set HTTP header for download transactions  
      \--header-upload stringArray          Set HTTP header for upload transactions  
      \--http-proxy string                  HTTP proxy URL  
      \--max-connections int                Maximum number of simultaneous backend API connections, 0 for unlimited  
      \--no-check-certificate               Do not verify the server SSL certificate (insecure)  
      \--no-gzip-encoding                   Don't set Accept-Encoding: gzip  
      \--timeout Duration                   IO idle timeout (default 5m0s)  
      \--tpslimit float                     Limit HTTP transactions per second to this  
      \--tpslimit-burst int                 Max burst of transactions for \--tpslimit (default 1\)  
      \--use-cookies                        Enable session cookiejar  
      \--user-agent string                  Set the user-agent to a specified string (default "rclone/v1.73.2")

## Performance

Flags helpful for increasing performance.

     \--buffer-size SizeSuffix   In memory buffer size when reading files for each \--transfer (default 16Mi)  
      \--checkers int             Number of checkers to run in parallel (default 8\)  
      \--transfers int            Number of file transfers to run in parallel (default 4\)

## Config

Flags for general configuration of rclone.

     \--ask-password                        Allow prompt for password for encrypted configuration (default true)  
      \--auto-confirm                        If enabled, do not request console confirmation  
      \--cache-dir string                    Directory rclone will use for caching (default "$HOME/.cache/rclone")  
      \--color AUTO|NEVER|ALWAYS             When to show colors (and other ANSI codes) AUTO|NEVER|ALWAYS (default AUTO)  
      \--config string                       Config file (default "$HOME/.config/rclone/rclone.conf")  
      \--default-time Time                   Time to show if modtime is unknown for files and directories (default 2000-01-01T00:00:00Z)  
      \--disable string                      Disable a comma separated list of features (use \--disable help to see a list)  
  \-n, \--dry-run                             Do a trial run with no permanent changes  
      \--error-on-no-transfer                Sets exit code 9 if no files are transferred, useful in scripts  
      \--fs-cache-expire-duration Duration   Cache remotes for this long (0 to disable caching) (default 5m0s)  
      \--fs-cache-expire-interval Duration   Interval to check for expired remotes (default 1m0s)  
      \--human-readable                      Print numbers in a human-readable format, sizes with suffix Ki|Mi|Gi|Ti|Pi  
  \-i, \--interactive                         Enable interactive mode  
      \--kv-lock-time Duration               Maximum time to keep key-value database locked by process (default 1s)  
      \--low-level-retries int               Number of low level retries to do (default 10\)  
      \--max-buffer-memory SizeSuffix        If set, don't allocate more than this amount of memory as buffers (default off)  
      \--no-console                          Hide console window (supported on Windows only)  
      \--no-unicode-normalization            Don't normalize unicode characters in filenames  
      \--password-command SpaceSepList       Command for supplying password for encrypted configuration  
      \--retries int                         Retry operations this many times if they fail (default 3\)  
      \--retries-sleep Duration              Interval between retrying operations if they fail, e.g. 500ms, 60s, 5m (0 to disable) (default 0s)  
      \--temp-dir string                     Directory rclone will use for temporary files (default "/tmp")  
      \--use-mmap                            Use mmap allocator (see docs)  
      \--use-server-modtime                  Use server modified time instead of object metadata

## Debugging

Flags for developers.

     \--cpuprofile string   Write cpu profile to file  
      \--dump DumpFlags      List of items to dump from: headers, bodies, requests, responses, auth, filters, goroutines, openfiles, mapper  
      \--dump-bodies         Dump HTTP headers and bodies \- may contain sensitive info  
      \--dump-headers        Dump HTTP headers \- may contain sensitive info  
      \--memprofile string   Write memory profile to file

## Filter

Flags for filtering directory listings.

     \--delete-excluded                     Delete files on dest excluded from sync  
      \--exclude stringArray                 Exclude files matching pattern  
      \--exclude-from stringArray            Read file exclude patterns from file (use \- to read from stdin)  
      \--exclude-if-present stringArray      Exclude directories if filename is present  
      \--files-from stringArray              Read list of source-file names from file (use \- to read from stdin)  
      \--files-from-raw stringArray          Read list of source-file names from file without any processing of lines (use \- to read from stdin)  
  \-f, \--filter stringArray                  Add a file filtering rule  
      \--filter-from stringArray             Read file filtering patterns from a file (use \- to read from stdin)  
      \--hash-filter string                  Partition filenames by hash k/n or randomly @/n  
      \--ignore-case                         Ignore case in filters (case insensitive)  
      \--include stringArray                 Include files matching pattern  
      \--include-from stringArray            Read file include patterns from file (use \- to read from stdin)  
      \--max-age Duration                    Only transfer files younger than this in s or suffix ms|s|m|h|d|w|M|y (default off)  
      \--max-depth int                       If set limits the recursion depth to this (default \-1)  
      \--max-size SizeSuffix                 Only transfer files smaller than this in KiB or suffix B|K|M|G|T|P (default off)  
      \--metadata-exclude stringArray        Exclude metadatas matching pattern  
      \--metadata-exclude-from stringArray   Read metadata exclude patterns from file (use \- to read from stdin)  
      \--metadata-filter stringArray         Add a metadata filtering rule  
      \--metadata-filter-from stringArray    Read metadata filtering patterns from a file (use \- to read from stdin)  
      \--metadata-include stringArray        Include metadatas matching pattern  
      \--metadata-include-from stringArray   Read metadata include patterns from file (use \- to read from stdin)  
      \--min-age Duration                    Only transfer files older than this in s or suffix ms|s|m|h|d|w|M|y (default off)  
      \--min-size SizeSuffix                 Only transfer files bigger than this in KiB or suffix B|K|M|G|T|P (default off)

## Listing

Flags for listing directories.

     \--default-time Time   Time to show if modtime is unknown for files and directories (default 2000-01-01T00:00:00Z)  
      \--fast-list           Use recursive list if available; uses more memory but fewer transactions

## Logging

Flags for logging and statistics.

     \--log-file string                     Log everything to this file  
      \--log-file-compress                   If set, compress rotated log files using gzip  
      \--log-file-max-age Duration           Maximum duration to retain old log files (eg "7d") (default 0s)  
      \--log-file-max-backups int            Maximum number of old log files to retain  
      \--log-file-max-size SizeSuffix        Maximum size of the log file before it's rotated (eg "10M") (default off)  
      \--log-format Bits                     Comma separated list of log format options (default date,time)  
      \--log-level LogLevel                  Log level DEBUG|INFO|NOTICE|ERROR (default NOTICE)  
      \--log-systemd                         Activate systemd integration for the logger  
      \--max-stats-groups int                Maximum number of stats groups to keep in memory, on max oldest is discarded (default 1000\)  
  \-P, \--progress                            Show progress during transfer  
      \--progress-terminal-title             Show progress on the terminal title (requires \-P/--progress)  
  \-q, \--quiet                               Print as little stuff as possible  
      \--stats Duration                      Interval between printing stats, e.g. 500ms, 60s, 5m (0 to disable) (default 1m0s)  
      \--stats-file-name-length int          Max file name length in stats (0 for no limit) (default 45\)  
      \--stats-log-level LogLevel            Log level to show \--stats output DEBUG|INFO|NOTICE|ERROR (default INFO)  
      \--stats-one-line                      Make the stats fit on one line  
      \--stats-one-line-date                 Enable \--stats-one-line and add current date/time prefix  
      \--stats-one-line-date-format string   Enable \--stats-one-line-date and use custom formatted date: Enclose date string in double quotes ("), see https://golang.org/pkg/time/\#Time.Format  
      \--stats-unit string                   Show data rate in stats as either 'bits' or 'bytes' per second (default "bytes")  
      \--syslog                              Use Syslog for logging  
      \--syslog-facility string              Facility for syslog, e.g. KERN,USER (default "DAEMON")  
      \--use-json-log                        Use json log format  
  \-v, \--verbose count                       Print lots more stuff (repeat for more)

## Metadata

Flags to control metadata.

 \-M, \--metadata                            If set, preserve metadata when copying objects  
      \--metadata-exclude stringArray        Exclude metadatas matching pattern  
      \--metadata-exclude-from stringArray   Read metadata exclude patterns from file (use \- to read from stdin)  
      \--metadata-filter stringArray         Add a metadata filtering rule  
      \--metadata-filter-from stringArray    Read metadata filtering patterns from a file (use \- to read from stdin)  
      \--metadata-include stringArray        Include metadatas matching pattern  
      \--metadata-include-from stringArray   Read metadata include patterns from file (use \- to read from stdin)  
      \--metadata-mapper SpaceSepList        Program to run to transforming metadata before upload  
      \--metadata-set stringArray            Add metadata key=value when uploading

## RC

Flags to control the Remote Control API.

     \--rc                                 Enable the remote control server  
      \--rc-addr stringArray                IPaddress:Port or :Port to bind server to (default localhost:5572)  
      \--rc-allow-origin string             Origin which cross-domain request (CORS) can be executed from  
      \--rc-baseurl string                  Prefix for URLs \- leave blank for root  
      \--rc-cert string                     TLS PEM key (concatenation of certificate and CA certificate)  
      \--rc-client-ca string                Client certificate authority to verify clients with  
      \--rc-enable-metrics                  Enable the Prometheus metrics path at the remote control server  
      \--rc-files string                    Path to local files to serve on the HTTP server  
      \--rc-htpasswd string                 A htpasswd file \- if not provided no authentication is done  
      \--rc-job-expire-duration Duration    Expire finished async jobs older than this value (default 1m0s)  
      \--rc-job-expire-interval Duration    Interval to check for expired async jobs (default 10s)  
      \--rc-key string                      TLS PEM Private key  
      \--rc-max-header-bytes int            Maximum size of request header (default 4096\)  
      \--rc-min-tls-version string          Minimum TLS version that is acceptable (default "tls1.0")  
      \--rc-no-auth                         Don't require auth for certain methods  
      \--rc-pass string                     Password for authentication  
      \--rc-realm string                    Realm for authentication  
      \--rc-salt string                     Password hashing salt (default "dlPL2MqE")  
      \--rc-serve                           Enable the serving of remote objects  
      \--rc-serve-no-modtime                Don't read the modification time (can speed things up)  
      \--rc-server-read-timeout Duration    Timeout for server reading data (default 1h0m0s)  
      \--rc-server-write-timeout Duration   Timeout for server writing data (default 1h0m0s)  
      \--rc-template string                 User-specified template  
      \--rc-user string                     User name for authentication  
      \--rc-user-from-header string         User name from a defined HTTP header  
      \--rc-web-fetch-url string            URL to fetch the releases for webgui (default "https://api.github.com/repos/rclone/rclone-webui-react/releases/latest")  
      \--rc-web-gui                         Launch WebGUI on localhost  
      \--rc-web-gui-force-update            Force update to latest version of web gui  
      \--rc-web-gui-no-open-browser         Don't open the browser automatically  
      \--rc-web-gui-update                  Check and update to latest version of web gui

## Metrics

Flags to control the Metrics HTTP endpoint..

     \--metrics-addr stringArray                IPaddress:Port or :Port to bind metrics server to  
      \--metrics-allow-origin string             Origin which cross-domain request (CORS) can be executed from  
      \--metrics-baseurl string                  Prefix for URLs \- leave blank for root  
      \--metrics-cert string                     TLS PEM key (concatenation of certificate and CA certificate)  
      \--metrics-client-ca string                Client certificate authority to verify clients with  
      \--metrics-htpasswd string                 A htpasswd file \- if not provided no authentication is done  
      \--metrics-key string                      TLS PEM Private key  
      \--metrics-max-header-bytes int            Maximum size of request header (default 4096\)  
      \--metrics-min-tls-version string          Minimum TLS version that is acceptable (default "tls1.0")  
      \--metrics-pass string                     Password for authentication  
      \--metrics-realm string                    Realm for authentication  
      \--metrics-salt string                     Password hashing salt (default "dlPL2MqE")  
      \--metrics-server-read-timeout Duration    Timeout for server reading data (default 1h0m0s)  
      \--metrics-server-write-timeout Duration   Timeout for server writing data (default 1h0m0s)  
      \--metrics-template string                 User-specified template  
      \--metrics-user string                     User name for authentication  
      \--metrics-user-from-header string         User name from a defined HTTP header  
      \--rc-enable-metrics                       Enable the Prometheus metrics path at the remote control server

## Backend

Backend-only flags (these can be set in the config file also).

     \--alias-description string                            Description of the remote  
      \--alias-remote string                                 Remote or path to alias  
      \--archive-description string                          Description of the remote  
      \--archive-remote string                               Remote to wrap to read archives from  
      \--azureblob-access-tier string                        Access tier of blob: hot, cool, cold or archive  
      \--azureblob-account string                            Azure Storage Account Name  
      \--azureblob-archive-tier-delete                       Delete archive tier blobs before overwriting  
      \--azureblob-chunk-size SizeSuffix                     Upload chunk size (default 4Mi)  
      \--azureblob-client-certificate-password string        Password for the certificate file (optional) (obscured)  
      \--azureblob-client-certificate-path string            Path to a PEM or PKCS12 certificate file including the private key  
      \--azureblob-client-id string                          The ID of the client in use  
      \--azureblob-client-secret string                      One of the service principal's client secrets  
      \--azureblob-client-send-certificate-chain             Send the certificate chain when using certificate auth  
      \--azureblob-connection-string string                  Storage Connection String  
      \--azureblob-copy-concurrency int                      Concurrency for multipart copy (default 512\)  
      \--azureblob-copy-cutoff SizeSuffix                    Cutoff for switching to multipart copy (default 8Mi)  
      \--azureblob-delete-snapshots string                   Set to specify how to deal with snapshots on blob deletion  
      \--azureblob-description string                        Description of the remote  
      \--azureblob-directory-markers                         Upload an empty object with a trailing slash when a new directory is created  
      \--azureblob-disable-checksum                          Don't store MD5 checksum with object metadata  
      \--azureblob-disable-instance-discovery                Skip requesting Microsoft Entra instance metadata  
      \--azureblob-encoding Encoding                         The encoding for the backend (default Slash,BackSlash,Del,Ctl,RightPeriod,InvalidUtf8)  
      \--azureblob-endpoint string                           Endpoint for the service  
      \--azureblob-env-auth                                  Read credentials from runtime (environment variables, CLI or MSI)  
      \--azureblob-key string                                Storage Account Shared Key  
      \--azureblob-list-chunk int                            Size of blob list (default 5000\)  
      \--azureblob-msi-client-id string                      Object ID of the user-assigned MSI to use, if any  
      \--azureblob-msi-mi-res-id string                      Azure resource ID of the user-assigned MSI to use, if any  
      \--azureblob-msi-object-id string                      Object ID of the user-assigned MSI to use, if any  
      \--azureblob-no-check-container                        If set, don't attempt to check the container exists or create it  
      \--azureblob-no-head-object                            If set, do not do HEAD before GET when getting objects  
      \--azureblob-password string                           The user's password (obscured)  
      \--azureblob-public-access string                      Public access level of a container: blob or container  
      \--azureblob-sas-url string                            SAS URL for container level access only  
      \--azureblob-service-principal-file string             Path to file containing credentials for use with a service principal  
      \--azureblob-tenant string                             ID of the service principal's tenant. Also called its directory ID  
      \--azureblob-upload-concurrency int                    Concurrency for multipart uploads (default 16\)  
      \--azureblob-upload-cutoff string                      Cutoff for switching to chunked upload (\<= 256 MiB) (deprecated)  
      \--azureblob-use-az                                    Use Azure CLI tool az for authentication  
      \--azureblob-use-copy-blob                             Whether to use the Copy Blob API when copying to the same storage account (default true)  
      \--azureblob-use-emulator                              Uses local storage emulator if provided as 'true'  
      \--azureblob-use-msi                                   Use a managed service identity to authenticate (only works in Azure)  
      \--azureblob-username string                           User name (usually an email address)  
      \--azurefiles-account string                           Azure Storage Account Name  
      \--azurefiles-chunk-size SizeSuffix                    Upload chunk size (default 4Mi)  
      \--azurefiles-client-certificate-password string       Password for the certificate file (optional) (obscured)  
      \--azurefiles-client-certificate-path string           Path to a PEM or PKCS12 certificate file including the private key  
      \--azurefiles-client-id string                         The ID of the client in use  
      \--azurefiles-client-secret string                     One of the service principal's client secrets  
      \--azurefiles-client-send-certificate-chain            Send the certificate chain when using certificate auth  
      \--azurefiles-connection-string string                 Storage Connection String  
      \--azurefiles-description string                       Description of the remote  
      \--azurefiles-disable-instance-discovery               Skip requesting Microsoft Entra instance metadata  
      \--azurefiles-encoding Encoding                        The encoding for the backend (default Slash,LtGt,DoubleQuote,Colon,Question,Asterisk,Pipe,BackSlash,Del,Ctl,RightPeriod,InvalidUtf8,Dot)  
      \--azurefiles-endpoint string                          Endpoint for the service  
      \--azurefiles-env-auth                                 Read credentials from runtime (environment variables, CLI or MSI)  
      \--azurefiles-key string                               Storage Account Shared Key  
      \--azurefiles-max-stream-size SizeSuffix               Max size for streamed files (default 10Gi)  
      \--azurefiles-msi-client-id string                     Object ID of the user-assigned MSI to use, if any  
      \--azurefiles-msi-mi-res-id string                     Azure resource ID of the user-assigned MSI to use, if any  
      \--azurefiles-msi-object-id string                     Object ID of the user-assigned MSI to use, if any  
      \--azurefiles-password string                          The user's password (obscured)  
      \--azurefiles-sas-url string                           SAS URL for container level access only  
      \--azurefiles-service-principal-file string            Path to file containing credentials for use with a service principal  
      \--azurefiles-share-name string                        Azure Files Share Name  
      \--azurefiles-tenant string                            ID of the service principal's tenant. Also called its directory ID  
      \--azurefiles-upload-concurrency int                   Concurrency for multipart uploads (default 16\)  
      \--azurefiles-use-az                                   Use Azure CLI tool az for authentication  
      \--azurefiles-use-emulator                             Uses local storage emulator if provided as 'true'  
      \--azurefiles-use-msi                                  Use a managed service identity to authenticate (only works in Azure)  
      \--azurefiles-username string                          User name (usually an email address)  
      \--b2-account string                                   Account ID or Application Key ID  
      \--b2-chunk-size SizeSuffix                            Upload chunk size (default 96Mi)  
      \--b2-copy-cutoff SizeSuffix                           Cutoff for switching to multipart copy (default 4Gi)  
      \--b2-description string                               Description of the remote  
      \--b2-disable-checksum                                 Disable checksums for large (\> upload cutoff) files  
      \--b2-download-auth-duration Duration                  Time before the public link authorization token will expire in s or suffix ms|s|m|h|d (default 1w)  
      \--b2-download-url string                              Custom endpoint for downloads  
      \--b2-encoding Encoding                                The encoding for the backend (default Slash,BackSlash,Del,Ctl,InvalidUtf8,Dot)  
      \--b2-endpoint string                                  Endpoint for the service  
      \--b2-hard-delete                                      Permanently delete files on remote removal, otherwise hide files  
      \--b2-key string                                       Application Key  
      \--b2-lifecycle int                                    Set the number of days deleted files should be kept when creating a bucket  
      \--b2-sse-customer-algorithm string                    If using SSE-C, the server-side encryption algorithm used when storing this object in B2  
      \--b2-sse-customer-key string                          To use SSE-C, you may provide the secret encryption key encoded in a UTF-8 compatible string to encrypt/decrypt your data  
      \--b2-sse-customer-key-base64 string                   To use SSE-C, you may provide the secret encryption key encoded in Base64 format to encrypt/decrypt your data  
      \--b2-sse-customer-key-md5 string                      If using SSE-C you may provide the secret encryption key MD5 checksum (optional)  
      \--b2-test-mode string                                 A flag string for X-Bz-Test-Mode header for debugging  
      \--b2-upload-concurrency int                           Concurrency for multipart uploads (default 4\)  
      \--b2-upload-cutoff SizeSuffix                         Cutoff for switching to chunked upload (default 200Mi)  
      \--b2-version-at Time                                  Show file versions as they were at the specified time (default off)  
      \--b2-versions                                         Include old versions in directory listings  
      \--box-access-token string                             Box App Primary Access Token  
      \--box-auth-url string                                 Auth server URL  
      \--box-box-config-file string                          Box App config.json location  
      \--box-box-sub-type string                              (default "user")  
      \--box-client-credentials                              Use client credentials OAuth flow  
      \--box-client-id string                                OAuth Client Id  
      \--box-client-secret string                            OAuth Client Secret  
      \--box-commit-retries int                              Max number of times to try committing a multipart file (default 100\)  
      \--box-description string                              Description of the remote  
      \--box-encoding Encoding                               The encoding for the backend (default Slash,BackSlash,Del,Ctl,RightSpace,InvalidUtf8,Dot)  
      \--box-impersonate string                              Impersonate this user ID when using a service account  
      \--box-list-chunk int                                  Size of listing chunk 1-1000 (default 1000\)  
      \--box-owned-by string                                 Only show items owned by the login (email address) passed in  
      \--box-root-folder-id string                           Fill in for rclone to use a non root folder as its starting point  
      \--box-token string                                    OAuth Access Token as a JSON blob  
      \--box-token-url string                                Token server url  
      \--box-upload-cutoff SizeSuffix                        Cutoff for switching to multipart upload (\>= 50 MiB) (default 50Mi)  
      \--cache-chunk-clean-interval Duration                 How often should the cache perform cleanups of the chunk storage (default 1m0s)  
      \--cache-chunk-no-memory                               Disable the in-memory cache for storing chunks during streaming  
      \--cache-chunk-path string                             Directory to cache chunk files (default "$HOME/.cache/rclone/cache-backend")  
      \--cache-chunk-size SizeSuffix                         The size of a chunk (partial file data) (default 5Mi)  
      \--cache-chunk-total-size SizeSuffix                   The total size that the chunks can take up on the local disk (default 10Gi)  
      \--cache-db-path string                                Directory to store file structure metadata DB (default "$HOME/.cache/rclone/cache-backend")  
      \--cache-db-purge                                      Clear all the cached data for this remote on start  
      \--cache-db-wait-time Duration                         How long to wait for the DB to be available \- 0 is unlimited (default 1s)  
      \--cache-description string                            Description of the remote  
      \--cache-info-age Duration                             How long to cache file structure information (directory listings, file size, times, etc.) (default 6h0m0s)  
      \--cache-plex-insecure string                          Skip all certificate verification when connecting to the Plex server  
      \--cache-plex-password string                          The password of the Plex user (obscured)  
      \--cache-plex-url string                               The URL of the Plex server  
      \--cache-plex-username string                          The username of the Plex user  
      \--cache-read-retries int                              How many times to retry a read from a cache storage (default 10\)  
      \--cache-remote string                                 Remote to cache  
      \--cache-rps int                                       Limits the number of requests per second to the source FS (-1 to disable) (default \-1)  
      \--cache-tmp-upload-path string                        Directory to keep temporary files until they are uploaded  
      \--cache-tmp-wait-time Duration                        How long should files be stored in local cache before being uploaded (default 15s)  
      \--cache-workers int                                   How many workers should run in parallel to download chunks (default 4\)  
      \--cache-writes                                        Cache file data on writes through the FS  
      \--chunker-chunk-size SizeSuffix                       Files larger than chunk size will be split in chunks (default 2Gi)  
      \--chunker-description string                          Description of the remote  
      \--chunker-fail-hard                                   Choose how chunker should handle files with missing or invalid chunks  
      \--chunker-hash-type string                            Choose how chunker handles hash sums (default "md5")  
      \--chunker-remote string                               Remote to chunk/unchunk  
      \--cloudinary-adjust-media-files-extensions            Cloudinary handles media formats as a file attribute and strips it from the name, which is unlike most other file systems (default true)  
      \--cloudinary-api-key string                           Cloudinary API Key  
      \--cloudinary-api-secret string                        Cloudinary API Secret  
      \--cloudinary-cloud-name string                        Cloudinary Environment Name  
      \--cloudinary-description string                       Description of the remote  
      \--cloudinary-encoding Encoding                        The encoding for the backend (default Slash,LtGt,DoubleQuote,Question,Asterisk,Pipe,Hash,Percent,BackSlash,Del,Ctl,RightSpace,InvalidUtf8,Dot)  
      \--cloudinary-eventually-consistent-delay Duration     Wait N seconds for eventual consistency of the databases that support the backend operation (default 0s)  
      \--cloudinary-media-extensions stringArray             Cloudinary supported media extensions (default 3ds,3g2,3gp,ai,arw,avi,avif,bmp,bw,cr2,cr3,djvu,dng,eps3,fbx,flif,flv,gif,glb,gltf,hdp,heic,heif,ico,indd,jp2,jpe,jpeg,jpg,jxl,jxr,m2ts,mov,mp4,mpeg,mts,mxf,obj,ogv,pdf,ply,png,psd,svg,tga,tif,tiff,ts,u3ma,usdz,wdp,webm,webp,wmv)  
      \--cloudinary-upload-prefix string                     Specify the API endpoint for environments out of the US  
      \--cloudinary-upload-preset string                     Upload Preset to select asset manipulation on upload  
      \--combine-description string                          Description of the remote  
      \--combine-upstreams SpaceSepList                      Upstreams for combining  
      \--compress-description string                         Description of the remote  
      \--compress-level string                               GZIP (levels \-2 to 9):  
      \--compress-mode string                                Compression mode (default "gzip")  
      \--compress-ram-cache-limit SizeSuffix                 Some remotes don't allow the upload of files with unknown size (default 20Mi)  
      \--compress-remote string                              Remote to compress  
  \-L, \--copy-links                                          Follow symlinks and copy the pointed to item  
      \--crypt-description string                            Description of the remote  
      \--crypt-directory-name-encryption                     Option to either encrypt directory names or leave them intact (default true)  
      \--crypt-filename-encoding string                      How to encode the encrypted filename to text string (default "base32")  
      \--crypt-filename-encryption string                    How to encrypt the filenames (default "standard")  
      \--crypt-no-data-encryption                            Option to either encrypt file data or leave it unencrypted  
      \--crypt-pass-bad-blocks                               If set this will pass bad blocks through as all 0  
      \--crypt-password string                               Password or pass phrase for encryption (obscured)  
      \--crypt-password2 string                              Password or pass phrase for salt (obscured)  
      \--crypt-remote string                                 Remote to encrypt/decrypt  
      \--crypt-server-side-across-configs                    Deprecated: use \--server-side-across-configs instead  
      \--crypt-show-mapping                                  For all files listed show how the names encrypt  
      \--crypt-strict-names                                  If set, this will raise an error when crypt comes across a filename that can't be decrypted  
      \--crypt-suffix string                                 If this is set it will override the default suffix of ".bin" (default ".bin")  
      \--doi-description string                              Description of the remote  
      \--doi-doi string                                      The DOI or the doi.org URL  
      \--doi-doi-resolver-api-url string                     The URL of the DOI resolver API to use  
      \--doi-provider string                                 DOI provider  
      \--drime-access-token string                           API Access token  
      \--drime-chunk-size SizeSuffix                         Chunk size to use for uploading (default 5Mi)  
      \--drime-description string                            Description of the remote  
      \--drime-encoding Encoding                             The encoding for the backend (default Slash,BackSlash,Del,Ctl,LeftSpace,RightSpace,InvalidUtf8,Dot)  
      \--drime-hard-delete                                   Delete files permanently rather than putting them into the trash  
      \--drime-list-chunk int                                Number of items to list in each call (default 1000\)  
      \--drime-root-folder-id string                         ID of the root folder  
      \--drime-upload-concurrency int                        Concurrency for multipart uploads and copies (default 4\)  
      \--drime-upload-cutoff SizeSuffix                      Cutoff for switching to chunked upload (default 200Mi)  
      \--drime-workspace-id string                           Account ID  
      \--drive-acknowledge-abuse                             Set to allow files which return cannotDownloadAbusiveFile to be downloaded  
      \--drive-allow-import-name-change                      Allow the filetype to change when uploading Google docs  
      \--drive-auth-owner-only                               Only consider files owned by the authenticated user  
      \--drive-auth-url string                               Auth server URL  
      \--drive-chunk-size SizeSuffix                         Upload chunk size (default 8Mi)  
      \--drive-client-credentials                            Use client credentials OAuth flow  
      \--drive-client-id string                              Google Application Client Id  
      \--drive-client-secret string                          OAuth Client Secret  
      \--drive-copy-shortcut-content                         Server side copy contents of shortcuts instead of the shortcut  
      \--drive-description string                            Description of the remote  
      \--drive-disable-http2                                 Disable drive using http2 (default true)  
      \--drive-encoding Encoding                             The encoding for the backend (default InvalidUtf8)  
      \--drive-env-auth                                      Get IAM credentials from runtime (environment variables or instance meta data if no env vars)  
      \--drive-export-formats string                         Comma separated list of preferred formats for downloading Google docs (default "docx,xlsx,pptx,svg")  
      \--drive-fast-list-bug-fix                             Work around a bug in Google Drive listing (default true)  
      \--drive-formats string                                Deprecated: See export\_formats  
      \--drive-impersonate string                            Impersonate this user when using a service account  
      \--drive-import-formats string                         Comma separated list of preferred formats for uploading Google docs  
      \--drive-keep-revision-forever                         Keep new head revision of each file forever  
      \--drive-list-chunk int                                Size of listing chunk 100-1000, 0 to disable (default 1000\)  
      \--drive-metadata-enforce-expansive-access             Whether the request should enforce expansive access rules  
      \--drive-metadata-labels Bits                          Control whether labels should be read or written in metadata (default off)  
      \--drive-metadata-owner Bits                           Control whether owner should be read or written in metadata (default read)  
      \--drive-metadata-permissions Bits                     Control whether permissions should be read or written in metadata (default off)  
      \--drive-pacer-burst int                               Number of API calls to allow without sleeping (default 100\)  
      \--drive-pacer-min-sleep Duration                      Minimum time to sleep between API calls (default 100ms)  
      \--drive-resource-key string                           Resource key for accessing a link-shared file  
      \--drive-root-folder-id string                         ID of the root folder  
      \--drive-scope string                                  Comma separated list of scopes that rclone should use when requesting access from drive  
      \--drive-server-side-across-configs                    Deprecated: use \--server-side-across-configs instead  
      \--drive-service-account-credentials string            Service Account Credentials JSON blob  
      \--drive-service-account-file string                   Service Account Credentials JSON file path  
      \--drive-shared-with-me                                Only show files that are shared with me  
      \--drive-show-all-gdocs                                Show all Google Docs including non-exportable ones in listings  
      \--drive-size-as-quota                                 Show sizes as storage quota usage, not actual size  
      \--drive-skip-checksum-gphotos                         Skip checksums on Google photos and videos only  
      \--drive-skip-dangling-shortcuts                       If set skip dangling shortcut files  
      \--drive-skip-gdocs                                    Skip google documents in all listings  
      \--drive-skip-shortcuts                                If set skip shortcut files  
      \--drive-starred-only                                  Only show files that are starred  
      \--drive-stop-on-download-limit                        Make download limit errors be fatal  
      \--drive-stop-on-upload-limit                          Make upload limit errors be fatal  
      \--drive-team-drive string                             ID of the Shared Drive (Team Drive)  
      \--drive-token string                                  OAuth Access Token as a JSON blob  
      \--drive-token-url string                              Token server url  
      \--drive-trashed-only                                  Only show files that are in the trash  
      \--drive-upload-cutoff SizeSuffix                      Cutoff for switching to chunked upload (default 8Mi)  
      \--drive-use-created-date                              Use file created date instead of modified date  
      \--drive-use-shared-date                               Use date file was shared instead of modified date  
      \--drive-use-trash                                     Send files to the trash instead of deleting permanently (default true)  
      \--drive-v2-download-min-size SizeSuffix               If Object's are greater, use drive v2 API to download (default off)  
      \--dropbox-auth-url string                             Auth server URL  
      \--dropbox-batch-mode string                           Upload file batching sync|async|off (default "sync")  
      \--dropbox-batch-size int                              Max number of files in upload batch  
      \--dropbox-batch-timeout Duration                      Max time to allow an idle upload batch before uploading (default 0s)  
      \--dropbox-chunk-size SizeSuffix                       Upload chunk size (\< 150Mi) (default 48Mi)  
      \--dropbox-client-credentials                          Use client credentials OAuth flow  
      \--dropbox-client-id string                            OAuth Client Id  
      \--dropbox-client-secret string                        OAuth Client Secret  
      \--dropbox-description string                          Description of the remote  
      \--dropbox-encoding Encoding                           The encoding for the backend (default Slash,BackSlash,Del,RightSpace,InvalidUtf8,Dot)  
      \--dropbox-export-formats CommaSepList                 Comma separated list of preferred formats for exporting files (default html,md)  
      \--dropbox-impersonate string                          Impersonate this user when using a business account  
      \--dropbox-pacer-min-sleep Duration                    Minimum time to sleep between API calls (default 10ms)  
      \--dropbox-root-namespace string                       Specify a different Dropbox namespace ID to use as the root for all paths  
      \--dropbox-shared-files                                Instructs rclone to work on individual shared files  
      \--dropbox-shared-folders                              Instructs rclone to work on shared folders  
      \--dropbox-show-all-exports                            Show all exportable files in listings  
      \--dropbox-skip-exports                                Skip exportable files in all listings  
      \--dropbox-token string                                OAuth Access Token as a JSON blob  
      \--dropbox-token-url string                            Token server url  
      \--fichier-api-key string                              Your API Key, get it from https://1fichier.com/console/params.pl  
      \--fichier-cdn                                         Set if you wish to use CDN download links  
      \--fichier-description string                          Description of the remote  
      \--fichier-encoding Encoding                           The encoding for the backend (default Slash,LtGt,DoubleQuote,SingleQuote,BackQuote,Dollar,BackSlash,Del,Ctl,LeftSpace,RightSpace,InvalidUtf8,Dot)  
      \--fichier-file-password string                        If you want to download a shared file that is password protected, add this parameter (obscured)  
      \--fichier-folder-password string                      If you want to list the files in a shared folder that is password protected, add this parameter (obscured)  
      \--fichier-shared-folder string                        If you want to download a shared folder, add this parameter  
      \--filefabric-description string                       Description of the remote  
      \--filefabric-encoding Encoding                        The encoding for the backend (default Slash,Del,Ctl,InvalidUtf8,Dot)  
      \--filefabric-permanent-token string                   Permanent Authentication Token  
      \--filefabric-root-folder-id string                    ID of the root folder  
      \--filefabric-token string                             Session Token  
      \--filefabric-token-expiry string                      Token expiry time  
      \--filefabric-url string                               URL of the Enterprise File Fabric to connect to  
      \--filefabric-version string                           Version read from the file fabric  
      \--filelu-chunk-size SizeSuffix                        Chunk size to use for uploading. Used for multipart uploads (default 64Mi)  
      \--filelu-description string                           Description of the remote  
      \--filelu-encoding Encoding                            The encoding for the backend (default Slash,LtGt,DoubleQuote,SingleQuote,BackQuote,Dollar,Colon,Question,Asterisk,Pipe,Hash,Percent,BackSlash,CrLf,Del,Ctl,LeftSpace,LeftPeriod,LeftTilde,LeftCrLfHtVt,RightSpace,RightPeriod,RightCrLfHtVt,InvalidUtf8,Dot,SquareBracket,Semicolon,Exclamation)  
      \--filelu-key string                                   Your FileLu Rclone key from My Account  
      \--filelu-upload-cutoff SizeSuffix                     Cutoff for switching to chunked upload. Any files larger than this will be uploaded in chunks of chunk\_size (default 500Mi)  
      \--filen-api-key string                                API Key for your Filen account (obscured)  
      \--filen-auth-version string                           Authentication Version (internal use only)  
      \--filen-base-folder-uuid string                       UUID of Account Root Directory (internal use only)  
      \--filen-description string                            Description of the remote  
      \--filen-email string                                  Email of your Filen account  
      \--filen-encoding Encoding                             The encoding for the backend (default Slash,Del,Ctl,InvalidUtf8,Dot)  
      \--filen-master-keys string                            Master Keys (internal use only)  
      \--filen-password string                               Password of your Filen account (obscured)  
      \--filen-private-key string                            Private RSA Key (internal use only)  
      \--filen-public-key string                             Public RSA Key (internal use only)  
      \--filen-upload-concurrency int                        Concurrency for chunked uploads (default 16\)  
      \--filescom-api-key string                             The API key used to authenticate with Files.com  
      \--filescom-description string                         Description of the remote  
      \--filescom-encoding Encoding                          The encoding for the backend (default Slash,BackSlash,Del,Ctl,RightSpace,RightCrLfHtVt,InvalidUtf8,Dot)  
      \--filescom-password string                            The password used to authenticate with Files.com (obscured)  
      \--filescom-site string                                Your site subdomain (e.g. mysite) or custom domain (e.g. myfiles.customdomain.com)  
      \--filescom-username string                            The username used to authenticate with Files.com  
      \--ftp-allow-insecure-tls-ciphers                      Allow insecure TLS ciphers  
      \--ftp-ask-password                                    Allow asking for FTP password when needed  
      \--ftp-close-timeout Duration                          Maximum time to wait for a response to close (default 1m0s)  
      \--ftp-concurrency int                                 Maximum number of FTP simultaneous connections, 0 for unlimited  
      \--ftp-description string                              Description of the remote  
      \--ftp-disable-epsv                                    Disable using EPSV even if server advertises support  
      \--ftp-disable-mlsd                                    Disable using MLSD even if server advertises support  
      \--ftp-disable-tls13                                   Disable TLS 1.3 (workaround for FTP servers with buggy TLS)  
      \--ftp-disable-utf8                                    Disable using UTF-8 even if server advertises support  
      \--ftp-encoding Encoding                               The encoding for the backend (default Slash,Del,Ctl,RightSpace,Dot)  
      \--ftp-explicit-tls                                    Use Explicit FTPS (FTP over TLS)  
      \--ftp-force-list-hidden                               Use LIST \-a to force listing of hidden files and folders. This will disable the use of MLSD  
      \--ftp-host string                                     FTP host to connect to  
      \--ftp-http-proxy string                               URL for HTTP CONNECT proxy  
      \--ftp-idle-timeout Duration                           Max time before closing idle connections (default 1m0s)  
      \--ftp-no-check-certificate                            Do not verify the TLS certificate of the server  
      \--ftp-no-check-upload                                 Don't check the upload is OK  
      \--ftp-pass string                                     FTP password (obscured)  
      \--ftp-port int                                        FTP port number (default 21\)  
      \--ftp-shut-timeout Duration                           Maximum time to wait for data connection closing status (default 1m0s)  
      \--ftp-socks-proxy string                              Socks 5 proxy host  
      \--ftp-tls                                             Use Implicit FTPS (FTP over TLS)  
      \--ftp-tls-cache-size int                              Size of TLS session cache for all control and data connections (default 32\)  
      \--ftp-user string                                     FTP username (default "$USER")  
      \--ftp-writing-mdtm                                    Use MDTM to set modification time (VsFtpd quirk)  
      \--gcs-access-token string                             Short-lived access token  
      \--gcs-anonymous                                       Access public buckets and objects without credentials  
      \--gcs-auth-url string                                 Auth server URL  
      \--gcs-bucket-acl string                               Access Control List for new buckets  
      \--gcs-bucket-policy-only                              Access checks should use bucket-level IAM policies  
      \--gcs-client-credentials                              Use client credentials OAuth flow  
      \--gcs-client-id string                                OAuth Client Id  
      \--gcs-client-secret string                            OAuth Client Secret  
      \--gcs-decompress                                      If set this will decompress gzip encoded objects  
      \--gcs-description string                              Description of the remote  
      \--gcs-directory-markers                               Upload an empty object with a trailing slash when a new directory is created  
      \--gcs-encoding Encoding                               The encoding for the backend (default Slash,CrLf,InvalidUtf8,Dot)  
      \--gcs-endpoint string                                 Custom endpoint for the storage API. Leave blank to use the provider default  
      \--gcs-env-auth                                        Get GCP IAM credentials from runtime (environment variables or instance meta data if no env vars)  
      \--gcs-location string                                 Location for the newly created buckets  
      \--gcs-no-check-bucket                                 If set, don't attempt to check the bucket exists or create it  
      \--gcs-object-acl string                               Access Control List for new objects  
      \--gcs-project-number string                           Project number  
      \--gcs-service-account-file string                     Service Account Credentials JSON file path  
      \--gcs-storage-class string                            The storage class to use when storing objects in Google Cloud Storage  
      \--gcs-token string                                    OAuth Access Token as a JSON blob  
      \--gcs-token-url string                                Token server url  
      \--gcs-user-project string                             User project  
      \--gofile-access-token string                          API Access token  
      \--gofile-account-id string                            Account ID  
      \--gofile-description string                           Description of the remote  
      \--gofile-encoding Encoding                            The encoding for the backend (default Slash,LtGt,DoubleQuote,Colon,Question,Asterisk,Pipe,BackSlash,Del,Ctl,LeftPeriod,RightPeriod,InvalidUtf8,Dot,Exclamation)  
      \--gofile-list-chunk int                               Number of items to list in each call (default 1000\)  
      \--gofile-root-folder-id string                        ID of the root folder  
      \--gphotos-auth-url string                             Auth server URL  
      \--gphotos-batch-mode string                           Upload file batching sync|async|off (default "sync")  
      \--gphotos-batch-size int                              Max number of files in upload batch  
      \--gphotos-batch-timeout Duration                      Max time to allow an idle upload batch before uploading (default 0s)  
      \--gphotos-client-credentials                          Use client credentials OAuth flow  
      \--gphotos-client-id string                            OAuth Client Id  
      \--gphotos-client-secret string                        OAuth Client Secret  
      \--gphotos-description string                          Description of the remote  
      \--gphotos-encoding Encoding                           The encoding for the backend (default Slash,CrLf,InvalidUtf8,Dot)  
      \--gphotos-include-archived                            Also view and download archived media  
      \--gphotos-proxy string                                Use the gphotosdl proxy for downloading the full resolution images  
      \--gphotos-read-only                                   Set to make the Google Photos backend read only  
      \--gphotos-read-size                                   Set to read the size of media items  
      \--gphotos-start-year int                              Year limits the photos to be downloaded to those which are uploaded after the given year (default 2000\)  
      \--gphotos-token string                                OAuth Access Token as a JSON blob  
      \--gphotos-token-url string                            Token server url  
      \--hasher-auto-size SizeSuffix                         Auto-update checksum for files smaller than this size (disabled by default)  
      \--hasher-description string                           Description of the remote  
      \--hasher-hashes CommaSepList                          Comma separated list of supported checksum types (default md5,sha1)  
      \--hasher-max-age Duration                             Maximum time to keep checksums in cache (0 \= no cache, off \= cache forever) (default off)  
      \--hasher-remote string                                Remote to cache checksums for (e.g. myRemote:path)  
      \--hdfs-data-transfer-protection string                Kerberos data transfer protection: authentication|integrity|privacy  
      \--hdfs-description string                             Description of the remote  
      \--hdfs-encoding Encoding                              The encoding for the backend (default Slash,Colon,Del,Ctl,InvalidUtf8,Dot)  
      \--hdfs-namenode CommaSepList                          Hadoop name nodes and ports  
      \--hdfs-service-principal-name string                  Kerberos service principal name for the namenode  
      \--hdfs-username string                                Hadoop user name  
      \--hidrive-auth-url string                             Auth server URL  
      \--hidrive-chunk-size SizeSuffix                       Chunksize for chunked uploads (default 48Mi)  
      \--hidrive-client-credentials                          Use client credentials OAuth flow  
      \--hidrive-client-id string                            OAuth Client Id  
      \--hidrive-client-secret string                        OAuth Client Secret  
      \--hidrive-description string                          Description of the remote  
      \--hidrive-disable-fetching-member-count               Do not fetch number of objects in directories unless it is absolutely necessary  
      \--hidrive-encoding Encoding                           The encoding for the backend (default Slash,Dot)  
      \--hidrive-endpoint string                             Endpoint for the service (default "https://api.hidrive.strato.com/2.1")  
      \--hidrive-root-prefix string                          The root/parent folder for all paths (default "/")  
      \--hidrive-scope-access string                         Access permissions that rclone should use when requesting access from HiDrive (default "rw")  
      \--hidrive-scope-role string                           User-level that rclone should use when requesting access from HiDrive (default "user")  
      \--hidrive-token string                                OAuth Access Token as a JSON blob  
      \--hidrive-token-url string                            Token server url  
      \--hidrive-upload-concurrency int                      Concurrency for chunked uploads (default 4\)  
      \--hidrive-upload-cutoff SizeSuffix                    Cutoff/Threshold for chunked uploads (default 96Mi)  
      \--http-description string                             Description of the remote  
      \--http-headers CommaSepList                           Set HTTP headers for all transactions  
      \--http-no-escape                                      Do not escape URL metacharacters in path names  
      \--http-no-head                                        Don't use HEAD requests  
      \--http-no-slash                                       Set this if the site doesn't end directories with /  
      \--http-url string                                     URL of HTTP host to connect to  
      \--iclouddrive-apple-id string                         Apple ID  
      \--iclouddrive-client-id string                        Client id (default "d39ba9916b7251055b22c7f910e2ea796ee65e98b2ddecea8f5dde8d9d1a815d")  
      \--iclouddrive-description string                      Description of the remote  
      \--iclouddrive-encoding Encoding                       The encoding for the backend (default Slash,BackSlash,Del,Ctl,InvalidUtf8,Dot)  
      \--iclouddrive-password string                         Password (obscured)  
      \--imagekit-description string                         Description of the remote  
      \--imagekit-encoding Encoding                          The encoding for the backend (default Slash,LtGt,DoubleQuote,Dollar,Question,Hash,Percent,BackSlash,Del,Ctl,InvalidUtf8,Dot,SquareBracket)  
      \--imagekit-endpoint string                            You can find your ImageKit.io URL endpoint in your \[dashboard\](https://imagekit.io/dashboard/developer/api-keys)  
      \--imagekit-only-signed Restrict unsigned image URLs   If you have configured Restrict unsigned image URLs in your dashboard settings, set this to true  
      \--imagekit-private-key string                         You can find your ImageKit.io private key in your \[dashboard\](https://imagekit.io/dashboard/developer/api-keys)  
      \--imagekit-public-key string                          You can find your ImageKit.io public key in your \[dashboard\](https://imagekit.io/dashboard/developer/api-keys)  
      \--imagekit-upload-tags string                         Tags to add to the uploaded files, e.g. "tag1,tag2"  
      \--imagekit-versions                                   Include old versions in directory listings  
      \--internetarchive-access-key-id string                IAS3 Access Key  
      \--internetarchive-description string                  Description of the remote  
      \--internetarchive-disable-checksum                    Don't ask the server to test against MD5 checksum calculated by rclone (default true)  
      \--internetarchive-encoding Encoding                   The encoding for the backend (default Slash,LtGt,CrLf,Del,Ctl,InvalidUtf8,Dot)  
      \--internetarchive-endpoint string                     IAS3 Endpoint (default "https://s3.us.archive.org")  
      \--internetarchive-front-endpoint string               Host of InternetArchive Frontend (default "https://archive.org")  
      \--internetarchive-item-derive                         Whether to trigger derive on the IA item or not. If set to false, the item will not be derived by IA upon upload (default true)  
      \--internetarchive-item-metadata stringArray           Metadata to be set on the IA item, this is different from file-level metadata that can be set using \--metadata-set  
      \--internetarchive-secret-access-key string            IAS3 Secret Key (password)  
      \--internetarchive-wait-archive Duration               Timeout for waiting the server's processing tasks (specifically archive and book\_op) to finish (default 0s)  
      \--internxt-description string                         Description of the remote  
      \--internxt-email string                               Email of your Internxt account  
      \--internxt-encoding Encoding                          The encoding for the backend (default Slash,BackSlash,CrLf,RightPeriod,InvalidUtf8,Dot)  
      \--internxt-pass string                                Password (obscured)  
      \--internxt-skip-hash-validation                       Skip hash validation when downloading files (default true)  
      \--jottacloud-auth-url string                          Auth server URL  
      \--jottacloud-client-credentials                       Use client credentials OAuth flow  
      \--jottacloud-client-id string                         OAuth Client Id  
      \--jottacloud-client-secret string                     OAuth Client Secret  
      \--jottacloud-description string                       Description of the remote  
      \--jottacloud-encoding Encoding                        The encoding for the backend (default Slash,LtGt,DoubleQuote,Colon,Question,Asterisk,Pipe,Del,Ctl,InvalidUtf8,Dot)  
      \--jottacloud-hard-delete                              Delete files permanently rather than putting them into the trash  
      \--jottacloud-md5-memory-limit SizeSuffix              Files bigger than this will be cached on disk to calculate the MD5 if required (default 10Mi)  
      \--jottacloud-no-versions                              Avoid server side versioning by deleting files and recreating files instead of overwriting them  
      \--jottacloud-token string                             OAuth Access Token as a JSON blob  
      \--jottacloud-token-url string                         Token server url  
      \--jottacloud-trashed-only                             Only show files that are in the trash  
      \--jottacloud-upload-resume-limit SizeSuffix           Files bigger than this can be resumed if the upload fail's (default 10Mi)  
      \--koofr-description string                            Description of the remote  
      \--koofr-encoding Encoding                             The encoding for the backend (default Slash,BackSlash,Del,Ctl,InvalidUtf8,Dot)  
      \--koofr-endpoint string                               The Koofr API endpoint to use  
      \--koofr-mountid string                                Mount ID of the mount to use  
      \--koofr-password string                               Your password for rclone generate one at https://app.koofr.net/app/admin/preferences/password (obscured)  
      \--koofr-provider string                               Choose your storage provider  
      \--koofr-setmtime                                      Does the backend support setting modification time (default true)  
      \--koofr-user string                                   Your user name  
      \--linkbox-description string                          Description of the remote  
      \--linkbox-token string                                Token from https://www.linkbox.to/admin/account  
      \--local-case-insensitive                              Force the filesystem to report itself as case insensitive  
      \--local-case-sensitive                                Force the filesystem to report itself as case sensitive  
      \--local-description string                            Description of the remote  
      \--local-encoding Encoding                             The encoding for the backend (default Slash,Dot)  
      \--local-hashes CommaSepList                           Comma separated list of supported checksum types  
      \--local-links                                         Translate symlinks to/from regular files with a '.rclonelink' extension for the local backend  
      \--local-no-check-updated                              Don't check to see if the files change during upload  
      \--local-no-clone                                      Disable reflink cloning for server-side copies  
      \--local-no-preallocate                                Disable preallocation of disk space for transferred files  
      \--local-no-set-modtime                                Disable setting modtime  
      \--local-no-sparse                                     Disable sparse files for multi-thread downloads  
      \--local-nounc                                         Disable UNC (long path names) conversion on Windows  
      \--local-time-type mtime|atime|btime|ctime             Set what kind of time is returned (default mtime)  
      \--local-unicode-normalization                         Apply unicode NFC normalization to paths and filenames  
      \--local-zero-size-links                               Assume the Stat size of links is zero (and read them instead) (deprecated)  
      \--mailru-auth-url string                              Auth server URL  
      \--mailru-check-hash                                   What should copy do if file checksum is mismatched or invalid (default true)  
      \--mailru-client-credentials                           Use client credentials OAuth flow  
      \--mailru-client-id string                             OAuth Client Id  
      \--mailru-client-secret string                         OAuth Client Secret  
      \--mailru-description string                           Description of the remote  
      \--mailru-encoding Encoding                            The encoding for the backend (default Slash,LtGt,DoubleQuote,Colon,Question,Asterisk,Pipe,BackSlash,Del,Ctl,InvalidUtf8,Dot)  
      \--mailru-pass string                                  Password (obscured)  
      \--mailru-speedup-enable                               Skip full upload if there is another file with same data hash (default true)  
      \--mailru-speedup-file-patterns string                 Comma separated list of file name patterns eligible for speedup (put by hash) (default "\*.mkv,\*.avi,\*.mp4,\*.mp3,\*.zip,\*.gz,\*.rar,\*.pdf")  
      \--mailru-speedup-max-disk SizeSuffix                  This option allows you to disable speedup (put by hash) for large files (default 3Gi)  
      \--mailru-speedup-max-memory SizeSuffix                Files larger than the size given below will always be hashed on disk (default 32Mi)  
      \--mailru-token string                                 OAuth Access Token as a JSON blob  
      \--mailru-token-url string                             Token server url  
      \--mailru-user string                                  User name (usually email)  
      \--mega-2fa string                                     The 2FA code of your MEGA account if the account is set up with one  
      \--mega-debug                                          Output more debug from Mega  
      \--mega-description string                             Description of the remote  
      \--mega-encoding Encoding                              The encoding for the backend (default Slash,InvalidUtf8,Dot)  
      \--mega-hard-delete                                    Delete files permanently rather than putting them into the trash  
      \--mega-pass string                                    Password (obscured)  
      \--mega-use-https                                      Use HTTPS for transfers  
      \--mega-user string                                    User name  
      \--memory-description string                           Description of the remote  
      \--memory-discard                                      If set all writes will be discarded and reads will return an error  
      \--netstorage-account string                           Set the NetStorage account name  
      \--netstorage-description string                       Description of the remote  
      \--netstorage-host string                              Domain+path of NetStorage host to connect to  
      \--netstorage-protocol string                          Select between HTTP or HTTPS protocol (default "https")  
      \--netstorage-secret string                            Set the NetStorage account secret/G2O key for authentication (obscured)  
  \-x, \--one-file-system                                     Don't cross filesystem boundaries (unix/macOS only)  
      \--onedrive-access-scopes SpaceSepList                 Set scopes to be requested by rclone (default Files.Read Files.ReadWrite Files.Read.All Files.ReadWrite.All Sites.Read.All offline\_access)  
      \--onedrive-auth-url string                            Auth server URL  
      \--onedrive-av-override                                Allows download of files the server thinks has a virus  
      \--onedrive-chunk-size SizeSuffix                      Chunk size to upload files with \- must be multiple of 320k (327,680 bytes) (default 10Mi)  
      \--onedrive-client-credentials                         Use client credentials OAuth flow  
      \--onedrive-client-id string                           OAuth Client Id  
      \--onedrive-client-secret string                       OAuth Client Secret  
      \--onedrive-delta                                      If set rclone will use delta listing to implement recursive listings  
      \--onedrive-description string                         Description of the remote  
      \--onedrive-drive-id string                            The ID of the drive to use  
      \--onedrive-drive-type string                          The type of the drive (personal | business | documentLibrary)  
      \--onedrive-encoding Encoding                          The encoding for the backend (default Slash,LtGt,DoubleQuote,Colon,Question,Asterisk,Pipe,BackSlash,Del,Ctl,LeftSpace,LeftTilde,RightSpace,RightPeriod,InvalidUtf8,Dot)  
      \--onedrive-expose-onenote-files                       Set to make OneNote files show up in directory listings  
      \--onedrive-hard-delete                                Permanently delete files on removal  
      \--onedrive-hash-type string                           Specify the hash in use for the backend (default "auto")  
      \--onedrive-link-password string                       Set the password for links created by the link command  
      \--onedrive-link-scope string                          Set the scope of the links created by the link command (default "anonymous")  
      \--onedrive-link-type string                           Set the type of the links created by the link command (default "view")  
      \--onedrive-list-chunk int                             Size of listing chunk (default 1000\)  
      \--onedrive-metadata-permissions Bits                  Control whether permissions should be read or written in metadata (default off)  
      \--onedrive-no-versions                                Remove all versions on modifying operations  
      \--onedrive-region string                              Choose national cloud region for OneDrive (default "global")  
      \--onedrive-root-folder-id string                      ID of the root folder  
      \--onedrive-server-side-across-configs                 Deprecated: use \--server-side-across-configs instead  
      \--onedrive-tenant string                              ID of the service principal's tenant. Also called its directory ID  
      \--onedrive-token string                               OAuth Access Token as a JSON blob  
      \--onedrive-token-url string                           Token server url  
      \--onedrive-upload-cutoff SizeSuffix                   Cutoff for switching to chunked upload (default off)  
      \--oos-attempt-resume-upload                           If true attempt to resume previously started multipart upload for the object  
      \--oos-chunk-size SizeSuffix                           Chunk size to use for uploading (default 5Mi)  
      \--oos-compartment string                              Specify compartment OCID, if you need to list buckets  
      \--oos-config-file string                              Path to OCI config file (default "\~/.oci/config")  
      \--oos-config-profile string                           Profile name inside the oci config file (default "Default")  
      \--oos-copy-cutoff SizeSuffix                          Cutoff for switching to multipart copy (default 4.656Gi)  
      \--oos-copy-timeout Duration                           Timeout for copy (default 1m0s)  
      \--oos-description string                              Description of the remote  
      \--oos-disable-checksum                                Don't store MD5 checksum with object metadata  
      \--oos-encoding Encoding                               The encoding for the backend (default Slash,InvalidUtf8,Dot)  
      \--oos-endpoint string                                 Endpoint for Object storage API  
      \--oos-leave-parts-on-error                            If true avoid calling abort upload on a failure, leaving all successfully uploaded parts for manual recovery  
      \--oos-max-upload-parts int                            Maximum number of parts in a multipart upload (default 10000\)  
      \--oos-namespace string                                Object storage namespace  
      \--oos-no-check-bucket                                 If set, don't attempt to check the bucket exists or create it  
      \--oos-provider string                                 Choose your Auth Provider (default "env\_auth")  
      \--oos-region string                                   Object storage Region  
      \--oos-sse-customer-algorithm string                   If using SSE-C, the optional header that specifies "AES256" as the encryption algorithm  
      \--oos-sse-customer-key string                         To use SSE-C, the optional header that specifies the base64-encoded 256-bit encryption key to use to  
      \--oos-sse-customer-key-file string                    To use SSE-C, a file containing the base64-encoded string of the AES-256 encryption key associated  
      \--oos-sse-customer-key-sha256 string                  If using SSE-C, The optional header that specifies the base64-encoded SHA256 hash of the encryption  
      \--oos-sse-kms-key-id string                           if using your own master key in vault, this header specifies the  
      \--oos-storage-tier string                             The storage class to use when storing new objects in storage. https://docs.oracle.com/en-us/iaas/Content/Object/Concepts/understandingstoragetiers.htm (default "Standard")  
      \--oos-upload-concurrency int                          Concurrency for multipart uploads (default 10\)  
      \--oos-upload-cutoff SizeSuffix                        Cutoff for switching to chunked upload (default 200Mi)  
      \--opendrive-access string                             Files and folders will be uploaded with this access permission (default private) (default "private")  
      \--opendrive-chunk-size SizeSuffix                     Files will be uploaded in chunks this size (default 10Mi)  
      \--opendrive-description string                        Description of the remote  
      \--opendrive-encoding Encoding                         The encoding for the backend (default Slash,LtGt,DoubleQuote,Colon,Question,Asterisk,Pipe,BackSlash,LeftSpace,LeftCrLfHtVt,RightSpace,RightCrLfHtVt,InvalidUtf8,Dot)  
      \--opendrive-password string                           Password (obscured)  
      \--opendrive-username string                           Username  
      \--pcloud-auth-url string                              Auth server URL  
      \--pcloud-client-credentials                           Use client credentials OAuth flow  
      \--pcloud-client-id string                             OAuth Client Id  
      \--pcloud-client-secret string                         OAuth Client Secret  
      \--pcloud-description string                           Description of the remote  
      \--pcloud-encoding Encoding                            The encoding for the backend (default Slash,BackSlash,Del,Ctl,InvalidUtf8,Dot)  
      \--pcloud-hostname string                              Hostname to connect to (default "api.pcloud.com")  
      \--pcloud-password string                              Your pcloud password (obscured)  
      \--pcloud-root-folder-id string                        Fill in for rclone to use a non root folder as its starting point (default "d0")  
      \--pcloud-token string                                 OAuth Access Token as a JSON blob  
      \--pcloud-token-url string                             Token server url  
      \--pcloud-username string                              Your pcloud username  
      \--pikpak-chunk-size SizeSuffix                        Chunk size for multipart uploads (default 5Mi)  
      \--pikpak-description string                           Description of the remote  
      \--pikpak-device-id string                             Device ID used for authorization  
      \--pikpak-encoding Encoding                            The encoding for the backend (default Slash,LtGt,DoubleQuote,Colon,Question,Asterisk,Pipe,BackSlash,Ctl,LeftSpace,RightSpace,RightPeriod,InvalidUtf8,Dot)  
      \--pikpak-hash-memory-limit SizeSuffix                 Files bigger than this will be cached on disk to calculate hash if required (default 10Mi)  
      \--pikpak-no-media-link                                Use original file links instead of media links  
      \--pikpak-pass string                                  Pikpak password (obscured)  
      \--pikpak-root-folder-id string                        ID of the root folder  
      \--pikpak-trashed-only                                 Only show files that are in the trash  
      \--pikpak-upload-concurrency int                       Concurrency for multipart uploads (default 4\)  
      \--pikpak-upload-cutoff SizeSuffix                     Cutoff for switching to chunked upload (default 200Mi)  
      \--pikpak-use-trash                                    Send files to the trash instead of deleting permanently (default true)  
      \--pikpak-user string                                  Pikpak username  
      \--pikpak-user-agent string                            HTTP user agent for pikpak (default "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0")  
      \--pixeldrain-api-key string                           API key for your pixeldrain account  
      \--pixeldrain-api-url string                           The API endpoint to connect to. In the vast majority of cases it's fine to leave (default "https://pixeldrain.com/api")  
      \--pixeldrain-description string                       Description of the remote  
      \--pixeldrain-root-folder-id string                    Root of the filesystem to use (default "me")  
      \--premiumizeme-auth-url string                        Auth server URL  
      \--premiumizeme-client-credentials                     Use client credentials OAuth flow  
      \--premiumizeme-client-id string                       OAuth Client Id  
      \--premiumizeme-client-secret string                   OAuth Client Secret  
      \--premiumizeme-description string                     Description of the remote  
      \--premiumizeme-encoding Encoding                      The encoding for the backend (default Slash,DoubleQuote,BackSlash,Del,Ctl,InvalidUtf8,Dot)  
      \--premiumizeme-token string                           OAuth Access Token as a JSON blob  
      \--premiumizeme-token-url string                       Token server url  
      \--protondrive-2fa string                              The 2FA code  
      \--protondrive-app-version string                      The app version string (default "macos-drive@1.0.0-alpha.1+rclone")  
      \--protondrive-description string                      Description of the remote  
      \--protondrive-enable-caching                          Caches the files and folders metadata to reduce API calls (default true)  
      \--protondrive-encoding Encoding                       The encoding for the backend (default Slash,LeftSpace,RightSpace,InvalidUtf8,Dot)  
      \--protondrive-mailbox-password string                 The mailbox password of your two-password proton account (obscured)  
      \--protondrive-original-file-size                      Return the file size before encryption (default true)  
      \--protondrive-otp-secret-key string                   The OTP secret key (obscured)  
      \--protondrive-password string                         The password of your proton account (obscured)  
      \--protondrive-replace-existing-draft                  Create a new revision when filename conflict is detected  
      \--protondrive-username string                         The username of your proton account  
      \--putio-auth-url string                               Auth server URL  
      \--putio-client-credentials                            Use client credentials OAuth flow  
      \--putio-client-id string                              OAuth Client Id  
      \--putio-client-secret string                          OAuth Client Secret  
      \--putio-description string                            Description of the remote  
      \--putio-encoding Encoding                             The encoding for the backend (default Slash,BackSlash,Del,Ctl,InvalidUtf8,Dot)  
      \--putio-token string                                  OAuth Access Token as a JSON blob  
      \--putio-token-url string                              Token server url  
      \--qingstor-access-key-id string                       QingStor Access Key ID  
      \--qingstor-chunk-size SizeSuffix                      Chunk size to use for uploading (default 4Mi)  
      \--qingstor-connection-retries int                     Number of connection retries (default 3\)  
      \--qingstor-description string                         Description of the remote  
      \--qingstor-encoding Encoding                          The encoding for the backend (default Slash,Ctl,InvalidUtf8)  
      \--qingstor-endpoint string                            Enter an endpoint URL to connection QingStor API  
      \--qingstor-env-auth                                   Get QingStor credentials from runtime  
      \--qingstor-secret-access-key string                   QingStor Secret Access Key (password)  
      \--qingstor-upload-concurrency int                     Concurrency for multipart uploads (default 1\)  
      \--qingstor-upload-cutoff SizeSuffix                   Cutoff for switching to chunked upload (default 200Mi)  
      \--qingstor-zone string                                Zone to connect to  
      \--quatrix-api-key string                              API key for accessing Quatrix account  
      \--quatrix-description string                          Description of the remote  
      \--quatrix-effective-upload-time string                Wanted upload time for one chunk (default "4s")  
      \--quatrix-encoding Encoding                           The encoding for the backend (default Slash,BackSlash,Del,Ctl,InvalidUtf8,Dot)  
      \--quatrix-hard-delete                                 Delete files permanently rather than putting them into the trash  
      \--quatrix-host string                                 Host name of Quatrix account  
      \--quatrix-maximal-summary-chunk-size SizeSuffix       The maximal summary for all chunks. It should not be less than 'transfers'\*'minimal\_chunk\_size' (default 95.367Mi)  
      \--quatrix-minimal-chunk-size SizeSuffix               The minimal size for one chunk (default 9.537Mi)  
      \--quatrix-skip-project-folders                        Skip project folders in operations  
      \--s3-access-key-id string                             AWS Access Key ID  
      \--s3-acl string                                       Canned ACL used when creating buckets and storing or copying objects  
      \--s3-bucket-acl string                                Canned ACL used when creating buckets  
      \--s3-chunk-size SizeSuffix                            Chunk size to use for uploading (default 5Mi)  
      \--s3-copy-cutoff SizeSuffix                           Cutoff for switching to multipart copy (default 4.656Gi)  
      \--s3-decompress                                       If set this will decompress gzip encoded objects  
      \--s3-description string                               Description of the remote  
      \--s3-directory-bucket                                 Set to use AWS Directory Buckets  
      \--s3-directory-markers                                Upload an empty object with a trailing slash when a new directory is created  
      \--s3-disable-checksum                                 Don't store MD5 checksum with object metadata  
      \--s3-disable-http2                                    Disable usage of http2 for S3 backends  
      \--s3-download-url string                              Custom endpoint for downloads  
      \--s3-encoding Encoding                                The encoding for the backend (default Slash,InvalidUtf8,Dot)  
      \--s3-endpoint string                                  Endpoint for S3 API  
      \--s3-env-auth                                         Get AWS credentials from runtime (environment variables or EC2/ECS meta data if no env vars)  
      \--s3-force-path-style                                 If true use path style access if false use virtual hosted style (default true)  
      \--s3-ibm-api-key string                               IBM API Key to be used to obtain IAM token  
      \--s3-ibm-resource-instance-id string                  IBM service instance id  
      \--s3-leave-parts-on-error                             If true avoid calling abort upload on a failure, leaving all successfully uploaded parts on S3 for manual recovery  
      \--s3-list-chunk int                                   Size of listing chunk (response list for each ListObject S3 request) (default 1000\)  
      \--s3-list-url-encode Tristate                         Whether to url encode listings: true/false/unset (default unset)  
      \--s3-list-version int                                 Version of ListObjects to use: 1,2 or 0 for auto  
      \--s3-location-constraint string                       Location constraint \- must be set to match the Region  
      \--s3-max-upload-parts int                             Maximum number of parts in a multipart upload (default 10000\)  
      \--s3-might-gzip Tristate                              Set this if the backend might gzip objects (default unset)  
      \--s3-no-check-bucket                                  If set, don't attempt to check the bucket exists or create it  
      \--s3-no-head                                          If set, don't HEAD uploaded objects to check integrity  
      \--s3-no-head-object                                   If set, do not do HEAD before GET when getting objects  
      \--s3-no-system-metadata                               Suppress setting and reading of system metadata  
      \--s3-profile string                                   Profile to use in the shared credentials file  
      \--s3-provider string                                  Choose your S3 provider  
      \--s3-region string                                    Region to connect to  
      \--s3-requester-pays                                   Enables requester pays option when interacting with S3 bucket  
      \--s3-role-arn string                                  ARN of the IAM role to assume  
      \--s3-role-external-id string                          External ID for assumed role  
      \--s3-role-session-duration string                     Session duration for assumed role  
      \--s3-role-session-name string                         Session name for assumed role  
      \--s3-sdk-log-mode Bits                                Set to debug the SDK (default Off)  
      \--s3-secret-access-key string                         AWS Secret Access Key (password)  
      \--s3-server-side-encryption string                    The server-side encryption algorithm used when storing this object in S3  
      \--s3-session-token string                             An AWS session token  
      \--s3-shared-credentials-file string                   Path to the shared credentials file  
      \--s3-sign-accept-encoding Tristate                    Set if rclone should include Accept-Encoding as part of the signature (default unset)  
      \--s3-sse-customer-algorithm string                    If using SSE-C, the server-side encryption algorithm used when storing this object in S3  
      \--s3-sse-customer-key string                          To use SSE-C you may provide the secret encryption key used to encrypt/decrypt your data  
      \--s3-sse-customer-key-base64 string                   If using SSE-C you must provide the secret encryption key encoded in base64 format to encrypt/decrypt your data  
      \--s3-sse-customer-key-md5 string                      If using SSE-C you may provide the secret encryption key MD5 checksum (optional)  
      \--s3-sse-kms-key-id string                            If using KMS ID you must provide the ARN of Key  
      \--s3-storage-class string                             The storage class to use when storing new objects in S3  
      \--s3-upload-concurrency int                           Concurrency for multipart uploads and copies (default 4\)  
      \--s3-upload-cutoff SizeSuffix                         Cutoff for switching to chunked upload (default 200Mi)  
      \--s3-use-accelerate-endpoint                          If true use the AWS S3 accelerated endpoint  
      \--s3-use-accept-encoding-gzip Accept-Encoding: gzip   Whether to send Accept-Encoding: gzip header (default unset)  
      \--s3-use-already-exists Tristate                      Set if rclone should report BucketAlreadyExists errors on bucket creation (default unset)  
      \--s3-use-arn-region                                   If true, enables arn region support for the service  
      \--s3-use-data-integrity-protections Tristate          If true use AWS S3 data integrity protections (default unset)  
      \--s3-use-dual-stack                                   If true use AWS S3 dual-stack endpoint (IPv6 support)  
      \--s3-use-multipart-etag Tristate                      Whether to use ETag in multipart uploads for verification (default unset)  
      \--s3-use-multipart-uploads Tristate                   Set if rclone should use multipart uploads (default unset)  
      \--s3-use-presigned-request                            Whether to use a presigned request or PutObject for single part uploads  
      \--s3-use-unsigned-payload Tristate                    Whether to use an unsigned payload in PutObject (default unset)  
      \--s3-use-x-id Tristate                                Set if rclone should add x-id URL parameters (default unset)  
      \--s3-v2-auth                                          If true use v2 authentication  
      \--s3-version-at Time                                  Show file versions as they were at the specified time (default off)  
      \--s3-version-deleted                                  Show deleted file markers when using versions  
      \--s3-versions                                         Include old versions in directory listings  
      \--seafile-2fa                                         Two-factor authentication ('true' if the account has 2FA enabled)  
      \--seafile-create-library                              Should rclone create a library if it doesn't exist  
      \--seafile-description string                          Description of the remote  
      \--seafile-encoding Encoding                           The encoding for the backend (default Slash,DoubleQuote,BackSlash,Ctl,InvalidUtf8,Dot)  
      \--seafile-library string                              Name of the library  
      \--seafile-library-key string                          Library password (for encrypted libraries only) (obscured)  
      \--seafile-pass string                                 Password (obscured)  
      \--seafile-url string                                  URL of seafile host to connect to  
      \--seafile-user string                                 User name (usually email address)  
      \--sftp-ask-password                                   Allow asking for SFTP password when needed  
      \--sftp-blake3sum-command string                       The command used to read BLAKE3 hashes  
      \--sftp-chunk-size SizeSuffix                          Upload and download chunk size (default 32Ki)  
      \--sftp-ciphers SpaceSepList                           Space separated list of ciphers to be used for session encryption, ordered by preference  
      \--sftp-concurrency int                                The maximum number of outstanding requests for one file (default 64\)  
      \--sftp-connections int                                Maximum number of SFTP simultaneous connections, 0 for unlimited  
      \--sftp-copy-is-hardlink                               Set to enable server side copies using hardlinks  
      \--sftp-crc32sum-command string                        The command used to read CRC-32 hashes  
      \--sftp-description string                             Description of the remote  
      \--sftp-disable-concurrent-reads                       If set don't use concurrent reads  
      \--sftp-disable-concurrent-writes                      If set don't use concurrent writes  
      \--sftp-disable-hashcheck                              Disable the execution of SSH commands to determine if remote file hashing is available  
      \--sftp-hashes CommaSepList                            Comma separated list of supported checksum types  
      \--sftp-host string                                    SSH host to connect to  
      \--sftp-host-key-algorithms SpaceSepList               Space separated list of host key algorithms, ordered by preference  
      \--sftp-http-proxy string                              URL for HTTP CONNECT proxy  
      \--sftp-idle-timeout Duration                          Max time before closing idle connections (default 1m0s)  
      \--sftp-key-exchange SpaceSepList                      Space separated list of key exchange algorithms, ordered by preference  
      \--sftp-key-file string                                Path to PEM-encoded private key file  
      \--sftp-key-file-pass string                           The passphrase to decrypt the PEM-encoded private key file (obscured)  
      \--sftp-key-pem string                                 Raw PEM-encoded private key  
      \--sftp-key-use-agent                                  When set forces the usage of the ssh-agent  
      \--sftp-known-hosts-file string                        Optional path to known\_hosts file  
      \--sftp-macs SpaceSepList                              Space separated list of MACs (message authentication code) algorithms, ordered by preference  
      \--sftp-md5sum-command string                          The command used to read MD5 hashes  
      \--sftp-pass string                                    SSH password, leave blank to use ssh-agent (obscured)  
      \--sftp-path-override string                           Override path used by SSH shell commands  
      \--sftp-port int                                       SSH port number (default 22\)  
      \--sftp-pubkey string                                  SSH public certificate for public certificate based authentication  
      \--sftp-pubkey-file string                             Optional path to public key file  
      \--sftp-server-command string                          Specifies the path or command to run a sftp server on the remote host  
      \--sftp-set-env SpaceSepList                           Environment variables to pass to sftp and commands  
      \--sftp-set-modtime                                    Set the modified time on the remote if set (default true)  
      \--sftp-sha1sum-command string                         The command used to read SHA-1 hashes  
      \--sftp-sha256sum-command string                       The command used to read SHA-256 hashes  
      \--sftp-shell-type string                              The type of SSH shell on remote server, if any  
      \--sftp-skip-links                                     Set to skip any symlinks and any other non regular files  
      \--sftp-socks-proxy string                             Socks 5 proxy host  
      \--sftp-ssh SpaceSepList                               Path and arguments to external ssh binary  
      \--sftp-subsystem string                               Specifies the SSH2 subsystem on the remote host (default "sftp")  
      \--sftp-use-fstat                                      If set use fstat instead of stat  
      \--sftp-use-insecure-cipher                            Enable the use of insecure ciphers and key exchange methods  
      \--sftp-user string                                    SSH username (default "$USER")  
      \--sftp-xxh128sum-command string                       The command used to read XXH128 hashes  
      \--sftp-xxh3sum-command string                         The command used to read XXH3 hashes  
      \--shade-api-key string                                An API key for your account  
      \--shade-chunk-size SizeSuffix                         Chunk size to use for uploading (default 64Mi)  
      \--shade-description string                            Description of the remote  
      \--shade-drive-id string                               The ID of your drive, see this in the drive settings. Individual rclone configs must be made per drive  
      \--shade-encoding Encoding                             The encoding for the backend (default Slash,BackSlash,Del,Ctl,InvalidUtf8,Dot)  
      \--shade-endpoint string                               Endpoint for the service  
      \--shade-max-upload-parts int                          Maximum amount of parts in a multipart upload (default 10000\)  
      \--shade-token string                                  JWT Token for performing Shade FS operations. Don't set this value \- rclone will set it automatically  
      \--shade-token-expiry string                           JWT Token Expiration time. Don't set this value \- rclone will set it automatically  
      \--shade-upload-concurrency int                        Concurrency for multipart uploads and copies. This is the number of chunks of the same file that are uploaded concurrently for multipart uploads and copies (default 4\)  
      \--sharefile-auth-url string                           Auth server URL  
      \--sharefile-chunk-size SizeSuffix                     Upload chunk size (default 64Mi)  
      \--sharefile-client-credentials                        Use client credentials OAuth flow  
      \--sharefile-client-id string                          OAuth Client Id  
      \--sharefile-client-secret string                      OAuth Client Secret  
      \--sharefile-description string                        Description of the remote  
      \--sharefile-encoding Encoding                         The encoding for the backend (default Slash,LtGt,DoubleQuote,Colon,Question,Asterisk,Pipe,BackSlash,Ctl,LeftSpace,LeftPeriod,RightSpace,RightPeriod,InvalidUtf8,Dot)  
      \--sharefile-endpoint string                           Endpoint for API calls  
      \--sharefile-root-folder-id string                     ID of the root folder  
      \--sharefile-token string                              OAuth Access Token as a JSON blob  
      \--sharefile-token-url string                          Token server url  
      \--sharefile-upload-cutoff SizeSuffix                  Cutoff for switching to multipart upload (default 128Mi)  
      \--sia-api-password string                             Sia Daemon API Password (obscured)  
      \--sia-api-url string                                  Sia daemon API URL, like http://sia.daemon.host:9980 (default "http://127.0.0.1:9980")  
      \--sia-description string                              Description of the remote  
      \--sia-encoding Encoding                               The encoding for the backend (default Slash,Question,Hash,Percent,Del,Ctl,InvalidUtf8,Dot)  
      \--sia-user-agent string                               Siad User Agent (default "Sia-Agent")  
      \--skip-links                                          Don't warn about skipped symlinks  
      \--skip-specials                                       Don't warn about skipped pipes, sockets and device objects  
      \--smb-case-insensitive                                Whether the server is configured to be case-insensitive (default true)  
      \--smb-description string                              Description of the remote  
      \--smb-domain string                                   Domain name for NTLM authentication (default "WORKGROUP")  
      \--smb-encoding Encoding                               The encoding for the backend (default Slash,LtGt,DoubleQuote,Colon,Question,Asterisk,Pipe,BackSlash,Ctl,RightSpace,RightPeriod,InvalidUtf8,Dot)  
      \--smb-hide-special-share                              Hide special shares (e.g. print$) which users aren't supposed to access (default true)  
      \--smb-host string                                     SMB server hostname to connect to  
      \--smb-idle-timeout Duration                           Max time before closing idle connections (default 1m0s)  
      \--smb-kerberos-ccache string                          Path to the Kerberos credential cache (krb5cc)  
      \--smb-pass string                                     SMB password (obscured)  
      \--smb-port int                                        SMB port number (default 445\)  
      \--smb-spn string                                      Service principal name  
      \--smb-use-kerberos                                    Use Kerberos authentication  
      \--smb-user string                                     SMB username (default "$USER")  
      \--storj-access-grant string                           Access grant  
      \--storj-api-key string                                API key  
      \--storj-description string                            Description of the remote  
      \--storj-passphrase string                             Encryption passphrase  
      \--storj-provider string                               Choose an authentication method (default "existing")  
      \--storj-satellite-address string                      Satellite address (default "us1.storj.io")  
      \--sugarsync-access-key-id string                      Sugarsync Access Key ID  
      \--sugarsync-app-id string                             Sugarsync App ID  
      \--sugarsync-authorization string                      Sugarsync authorization  
      \--sugarsync-authorization-expiry string               Sugarsync authorization expiry  
      \--sugarsync-deleted-id string                         Sugarsync deleted folder id  
      \--sugarsync-description string                        Description of the remote  
      \--sugarsync-encoding Encoding                         The encoding for the backend (default Slash,Ctl,InvalidUtf8,Dot)  
      \--sugarsync-hard-delete                               Permanently delete files if true  
      \--sugarsync-private-access-key string                 Sugarsync Private Access Key  
      \--sugarsync-refresh-token string                      Sugarsync refresh token  
      \--sugarsync-root-id string                            Sugarsync root id  
      \--sugarsync-user string                               Sugarsync user  
      \--swift-application-credential-id string              Application Credential ID (OS\_APPLICATION\_CREDENTIAL\_ID)  
      \--swift-application-credential-name string            Application Credential Name (OS\_APPLICATION\_CREDENTIAL\_NAME)  
      \--swift-application-credential-secret string          Application Credential Secret (OS\_APPLICATION\_CREDENTIAL\_SECRET)  
      \--swift-auth string                                   Authentication URL for server (OS\_AUTH\_URL)  
      \--swift-auth-token string                             Auth Token from alternate authentication \- optional (OS\_AUTH\_TOKEN)  
      \--swift-auth-version int                              AuthVersion \- optional \- set to (1,2,3) if your auth URL has no version (ST\_AUTH\_VERSION)  
      \--swift-chunk-size SizeSuffix                         Above this size files will be chunked (default 5Gi)  
      \--swift-description string                            Description of the remote  
      \--swift-domain string                                 User domain \- optional (v3 auth) (OS\_USER\_DOMAIN\_NAME)  
      \--swift-encoding Encoding                             The encoding for the backend (default Slash,InvalidUtf8)  
      \--swift-endpoint-type string                          Endpoint type to choose from the service catalogue (OS\_ENDPOINT\_TYPE) (default "public")  
      \--swift-env-auth                                      Get swift credentials from environment variables in standard OpenStack form  
      \--swift-fetch-until-empty-page                        When paginating, always fetch unless we received an empty page  
      \--swift-key string                                    API key or password (OS\_PASSWORD)  
      \--swift-leave-parts-on-error                          If true avoid calling abort upload on a failure  
      \--swift-no-chunk                                      Don't chunk files during streaming upload  
      \--swift-no-large-objects                              Disable support for static and dynamic large objects  
      \--swift-partial-page-fetch-threshold int              When paginating, fetch if the current page is within this percentage of the limit  
      \--swift-region string                                 Region name \- optional (OS\_REGION\_NAME)  
      \--swift-storage-policy string                         The storage policy to use when creating a new container  
      \--swift-storage-url string                            Storage URL \- optional (OS\_STORAGE\_URL)  
      \--swift-tenant string                                 Tenant name \- optional for v1 auth, this or tenant\_id required otherwise (OS\_TENANT\_NAME or OS\_PROJECT\_NAME)  
      \--swift-tenant-domain string                          Tenant domain \- optional (v3 auth) (OS\_PROJECT\_DOMAIN\_NAME)  
      \--swift-tenant-id string                              Tenant ID \- optional for v1 auth, this or tenant required otherwise (OS\_TENANT\_ID)  
      \--swift-use-segments-container Tristate               Choose destination for large object segments (default unset)  
      \--swift-user string                                   User name to log in (OS\_USERNAME)  
      \--swift-user-id string                                User ID to log in \- optional \- most swift systems use user and leave this blank (v3 auth) (OS\_USER\_ID)  
      \--ulozto-app-token string                             The application token identifying the app. An app API key can be either found in the API  
      \--ulozto-description string                           Description of the remote  
      \--ulozto-encoding Encoding                            The encoding for the backend (default Slash,BackSlash,Del,Ctl,InvalidUtf8,Dot)  
      \--ulozto-list-page-size int                           The size of a single page for list commands. 1-500 (default 500\)  
      \--ulozto-password string                              The password for the user (obscured)  
      \--ulozto-root-folder-slug string                      If set, rclone will use this folder as the root folder for all operations. For example,  
      \--ulozto-username string                              The username of the principal to operate as  
      \--union-action-policy string                          Policy to choose upstream on ACTION category (default "epall")  
      \--union-cache-time int                                Cache time of usage and free space (in seconds) (default 120\)  
      \--union-create-policy string                          Policy to choose upstream on CREATE category (default "epmfs")  
      \--union-description string                            Description of the remote  
      \--union-min-free-space SizeSuffix                     Minimum viable free space for lfs/eplfs policies (default 1Gi)  
      \--union-search-policy string                          Policy to choose upstream on SEARCH category (default "ff")  
      \--union-upstreams string                              List of space separated upstreams  
      \--webdav-auth-redirect                                Preserve authentication on redirect  
      \--webdav-bearer-token string                          Bearer token instead of user/pass (e.g. a Macaroon)  
      \--webdav-bearer-token-command string                  Command to run to get a bearer token  
      \--webdav-description string                           Description of the remote  
      \--webdav-encoding string                              The encoding for the backend  
      \--webdav-headers CommaSepList                         Set HTTP headers for all transactions  
      \--webdav-nextcloud-chunk-size SizeSuffix              Nextcloud upload chunk size (default 10Mi)  
      \--webdav-owncloud-exclude-mounts                      Exclude ownCloud mounted storages  
      \--webdav-owncloud-exclude-shares                      Exclude ownCloud shares  
      \--webdav-pacer-min-sleep Duration                     Minimum time to sleep between API calls (default 10ms)  
      \--webdav-pass string                                  Password (obscured)  
      \--webdav-unix-socket string                           Path to a unix domain socket to dial to, instead of opening a TCP connection directly  
      \--webdav-url string                                   URL of http host to connect to  
      \--webdav-user string                                  User name  
      \--webdav-vendor string                                Name of the WebDAV site/service/software you are using  
      \--yandex-auth-url string                              Auth server URL  
      \--yandex-client-credentials                           Use client credentials OAuth flow  
      \--yandex-client-id string                             OAuth Client Id  
      \--yandex-client-secret string                         OAuth Client Secret  
      \--yandex-description string                           Description of the remote  
      \--yandex-encoding Encoding                            The encoding for the backend (default Slash,Del,Ctl,InvalidUtf8,Dot)  
      \--yandex-hard-delete                                  Delete files permanently rather than putting them into the trash  
      \--yandex-spoof-ua                                     Set the user agent to match an official version of the yandex disk client. May help with upload performance (default true)  
      \--yandex-token string                                 OAuth Access Token as a JSON blob  
      \--yandex-token-url string                             Token server url  
      \--zoho-auth-url string                                Auth server URL  
      \--zoho-client-credentials                             Use client credentials OAuth flow  
      \--zoho-client-id string                               OAuth Client Id  
      \--zoho-client-secret string                           OAuth Client Secret  
      \--zoho-description string                             Description of the remote  
      \--zoho-encoding Encoding                              The encoding for the backend (default Del,Ctl,InvalidUtf8)  
      \--zoho-region string                                  Zoho region to connect to  
      \--zoho-token string                                   OAuth Access Token as a JSON blob  
      \--zoho-token-url string                               Token server url  
      \--zoho-upload-cutoff SizeSuffix                       Cutoff for switching to large file upload api (\>= 10 MiB) (default 10Mi)

# rclone config

Enter an interactive configuration session.

## Synopsis

Enter an interactive configuration session where you can setup new remotes and manage existing ones. You may also set or remove a password to protect your configuration.

rclone config \[flags\]

## Options

 \-h, \--help   help for config

See the [global flags page](https://rclone.org/flags/) for global options not listed here.

## See Also

* [rclone](https://rclone.org/commands/rclone/) \- Show help for rclone commands, flags and backends.  
* [rclone config create](https://rclone.org/commands/rclone_config_create/) \- Create a new remote with name, type and options.  
* [rclone config delete](https://rclone.org/commands/rclone_config_delete/) \- Delete an existing remote.  
* [rclone config disconnect](https://rclone.org/commands/rclone_config_disconnect/) \- Disconnects user from remote  
* [rclone config dump](https://rclone.org/commands/rclone_config_dump/) \- Dump the config file as JSON.  
* [rclone config edit](https://rclone.org/commands/rclone_config_edit/) \- Enter an interactive configuration session.  
* [rclone config encryption](https://rclone.org/commands/rclone_config_encryption/) \- set, remove and check the encryption for the config file  
* [rclone config file](https://rclone.org/commands/rclone_config_file/) \- Show path of configuration file in use.  
* [rclone config password](https://rclone.org/commands/rclone_config_password/) \- Update password in an existing remote.  
* [rclone config paths](https://rclone.org/commands/rclone_config_paths/) \- Show paths used for configuration, cache, temp etc.  
* [rclone config providers](https://rclone.org/commands/rclone_config_providers/) \- List in JSON format all the providers and options.  
* [rclone config reconnect](https://rclone.org/commands/rclone_config_reconnect/) \- Re-authenticates user with remote.  
* [rclone config redacted](https://rclone.org/commands/rclone_config_redacted/) \- Print redacted (decrypted) config file, or the redacted config for a single remote.  
* [rclone config show](https://rclone.org/commands/rclone_config_show/) \- Print (decrypted) config file, or the config for a single remote.  
* [rclone config string](https://rclone.org/commands/rclone_config_string/) \- Print connection string for a single remote.  
* [rclone config touch](https://rclone.org/commands/rclone_config_touch/) \- Ensure configuration file exists.  
* [rclone config update](https://rclone.org/commands/rclone_config_update/) \- Update options in an existing remote.  
* [rclone config userinfo](https://rclone.org/commands/rclone_config_userinfo/) \- Prints info about logged in user of remote.

# rclone config create

Create a new remote with name, type and options.

## Synopsis

Create a new remote of name with type and options. The options should be passed in pairs of key value or as key=value.

For example, to make a swift remote of name myremote using auto config you would do:

rclone config create myremote swift env\_auth true

rclone config create myremote swift env\_auth\=true

So for example if you wanted to configure a Google Drive remote but using remote authorization you would do this:

rclone config create mydrive drive config\_is\_local\=false

Note that if the config process would normally ask a question the default is taken (unless \--non-interactive is used). Each time that happens rclone will print or DEBUG a message saying how to affect the value taken.

If any of the parameters passed is a password field, then rclone will automatically obscure them if they aren't already obscured before putting them in the config file.

NB If the password parameter is 22 characters or longer and consists only of base64 characters then rclone can get confused about whether the password is already obscured or not and put unobscured passwords into the config file. If you want to be 100% certain that the passwords get obscured then use the \--obscure flag, or if you are 100% certain you are already passing obscured passwords then use \--no-obscure. You can also set obscured passwords using the rclone config password command.

The flag \--non-interactive is for use by applications that wish to configure rclone themselves, rather than using rclone's text based configuration questions. If this flag is set, and rclone needs to ask the user a question, a JSON blob will be returned with the question in it.

This will look something like (some irrelevant detail removed):

{

 "State": "\*oauth-islocal,teamdrive,,",

 "Option": {

   "Name": "config\_is\_local",

   "Help": "Use web browser to automatically authenticate rclone with remote?\\n \* Say Y if the machine running rclone has a web browser you can use\\n \* Say N if running rclone on a (remote) machine without web browser access\\nIf not sure try Y. If Y failed, try N.\\n",

   "Default": true,

   "Examples": \[

     {

       "Value": "true",

       "Help": "Yes"

     },

     {

       "Value": "false",

       "Help": "No"

     }

   \],

   "Required": false,

   "IsPassword": false,

   "Type": "bool",

   "Exclusive": true,

 },

 "Error": "",

}

The format of Option is the same as returned by rclone config providers. The question should be asked to the user and returned to rclone as the \--result option along with the \--state parameter.

The keys of Option are used as follows:

* Name \- name of variable \- show to user  
* Help \- help text. Hard wrapped at 80 chars. Any URLs should be clicky.  
* Default \- default value \- return this if the user just wants the default.  
* Examples \- the user should be able to choose one of these  
* Required \- the value should be non-empty  
* IsPassword \- the value is a password and should be edited as such  
* Type \- type of value, eg bool, string, int and others  
* Exclusive \- if set no free-form entry allowed only the Examples  
* Irrelevant keys Provider, ShortOpt, Hide, NoPrefix, Advanced

If Error is set then it should be shown to the user at the same time as the question.

rclone config update name \--continue \--state "\*oauth-islocal,teamdrive,," \--result "true"

Note that when using \--continue all passwords should be passed in the clear (not obscured). Any default config values should be passed in with each invocation of \--continue.

At the end of the non interactive process, rclone will return a result with State as empty string.

If \--all is passed then rclone will ask all the config questions, not just the post config questions. Any parameters are used as defaults for questions as usual.

Note that bin/config.py in the rclone source implements this protocol as a readable demonstration.

rclone config create name type \[key value\]\* \[flags\]

## Options

     \--all               Ask the full set of config questions  
      \--continue          Continue the configuration process with an answer  
  \-h, \--help              help for create  
      \--no-obscure        Force any passwords not to be obscured  
      \--no-output         Don't provide any output  
      \--non-interactive   Don't interact with user and return questions  
      \--obscure           Force any passwords to be obscured  
      \--result string     Result \- use with \--continue  
      \--state string      State \- use with \--continue

See the [global flags page](https://rclone.org/flags/) for global options not listed here.

# rclone config providers

List in JSON format all the providers and options.

rclone config providers \[flags\]

## Options

 \-h, \--help   help for providers

See the [global flags page](https://rclone.org/flags/) for global options not listed here.

