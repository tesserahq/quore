# Secure, Extensible Credential Management System Design

## System Overview and Goals

We are designing a secure and extensible credential management system for a FastAPI-based platform, inspired by n8n’s approach to credentials. The system will allow the platform to store and use sensitive access credentials (API tokens, SSH keys, etc.) for connecting to external services (GitHub, GitLab, etc.) in a safe and flexible manner. Key goals include:

* Dynamic Credential Schema: Define credential types with a schema (fields, labels, help text, field types) so that UIs can generate forms dynamically (similar to n8n’s credential modals).
* Extensibility: Use a class-based registry pattern to easily add new credential types (plugins can register new credential classes with their metadata and field requirements).
* Secure Storage: Encrypt all sensitive credential data at rest in a PostgreSQL database using strong symmetric encryption (e.g. Fernet/AES) with a master key kept out of the DB.
* Plugin Integration: Allow each plugin registration to explicitly reference a named credential. When a plugin (e.g. a workflow integration or a Git-based plugin) is registered, it can specify which stored credential to use for actions like cloning a private Git repo.
* Multiple Credential Types: Support various credential types from the start (GitHub PAT, GitLab PAT/OAuth token, SSH key for Git, etc.) and allow new types to be added later.
* Sharing and Reuse: Allow optional sharing of credentials between workspaces or projects. Credentials can be marked as reusable (shared) so that others can use them without seeing the secret values.
* Usability: Make the system easy to reason about for developers and to present in a UI (forms are generated from schemas, similar to n8n’s UI for credentials).

## Credential Types and Dynamic Schema

Credential types are defined as classes or schemas that specify what fields are required for that type of credential. Each credential type includes metadata for UI form generation, such as field labels, input types, and help text. This is similar to n8n’s approach where each credential has a name, display name, and a list of properties (fields) with types and descriptions ￼. For example, a GitHub Personal Access Token (PAT) credential might be defined with one field for the token string, whereas an SSH Key credential type might require a private key and an optional passphrase.

We needs to represent the schema in a JSON-schema-like structure or via Pydantic models. For instance, we might define a credential type’s fields like so:

```
# Example schema definitions for credential types
github_pat_fields = [
    {
        "name": "token",
        "label": "Personal Access Token",
        "type": "string",
        "input_type": "password",      # UI should render a password field
        "help": "GitHub PAT with repo scope",
        "required": True
    }
]

gitlab_pat_fields = [
    {
        "name": "token",
        "label": "GitLab Personal Access Token",
        "type": "string",
        "input_type": "password",
        "help": "GitLab PAT with API scope",
        "required": True
    }
    # (Could also support OAuth token fields in a separate credential type)
]

ssh_key_fields = [
    {
        "name": "private_key",
        "label": "SSH Private Key",
        "type": "string",
        "input_type": "textarea",     # multi-line text area for key
        "help": "Private SSH key (e.g., RSA) for Git access",
        "required": True
    },
    {
        "name": "passphrase",
        "label": "Key Passphrase",
        "type": "string",
        "input_type": "password",
        "help": "Passphrase for the SSH key (leave blank if none)",
        "required": False
    }
]
```

Each field entry includes a human-friendly label, an internal name (key), a data type (string, boolean, etc.), an input_type hint for the UI (e.g. password vs. normal text, textarea for multiline), whether it’s required, and optional help text to guide users. This schema approach means the front-end can query the backend for the schema of a given credential type and dynamically render a form for it, just as n8n’s Credentials UI does. In n8n, for example, credential classes define a properties list where each field has a displayName, internal name, type, etc. ￼. We mirror that idea with our JSON schema for fields.

Using Pydantic models is another effective approach: each credential type can be a Pydantic model defining its fields, using Pydantic’s Field to add metadata like title (label) and description (help text). For example:

```python
from pydantic import BaseModel, SecretStr, Field

class GithubPATModel(BaseModel):
    token: SecretStr = Field(..., title="Personal Access Token", description="GitHub PAT with repo access")

class GitlabPATModel(BaseModel):
    token: SecretStr = Field(..., title="GitLab Personal Access Token", description="GitLab PAT with API scope")

class SSHKeyModel(BaseModel):
    private_key: SecretStr = Field(..., title="SSH Private Key", description="Private SSH key content")
    passphrase: SecretStr | None = Field(None, title="Key Passphrase", description="Passphrase for the SSH key")
```

These Pydantic models automatically produce a JSON Schema (used by FastAPI’s documentation) that could be leveraged for UI generation. The use of SecretStr ensures that if these models are printed or returned, the secret fields are not accidentally exposed (they display as "***" when converted to string), adding a safety layer for logging and serialization in the API ￼ ￼. Each credential type model can be converted to a generic schema for the front-end if needed.

## Class-Based Credential Registry (Extensibility)

To make the system extensible, we employ a class-based registry pattern. Each credential type is a Python class that registers itself (or is registered in a central registry) with a unique type name and its schema/metadata. This allows new credential types to be added by simply defining a new subclass, without modifying central logic.

For example, we can have a base class CredentialType that new credential classes inherit from:

```python
credential_registry = {}

class CredentialType:
    type_name: str            # unique key, e.g. "github_pat"
    display_name: str         # human-readable, e.g. "GitHub PAT"
    fields: list              # list of field definitions (as above)

    def __init_subclass__(cls, **kwargs):
        """Automatically register subclass in the registry by type_name."""
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "type_name"):
            credential_registry[cls.type_name] = cls

# Example subclass for GitHub PAT
class GithubPATCredential(CredentialType):
    type_name = "github_pat"
    display_name = "GitHub Personal Access Token"
    fields = github_pat_fields  # from the schema defined earlier
```

In this pattern, when the GithubPATCredential class is defined, it gets added to the credential_registry. The registry might map the type_name to the class (or to an instance if needed). Whenever the system needs to know what credential types are available (for API or UI), it can list the keys in this registry and their metadata. This makes it easy to add new credential types: for instance, adding a SlackAPIKeyCredential class with its fields would automatically become available.

The credential class could also carry methods relevant to that type. For example, a credential class might define how to use those credentials (though usage can often be handled externally). We could imagine a method like authenticate() or similar, but for our purposes, the main responsibility is to define the schema and perhaps validate the fields. By using this registry approach, extensibility is achieved: new credential types register themselves with their name, display name, and field requirements.

## Secure Storage and Encryption of Secrets

Security is paramount: all credential secret values should be encrypted at rest in the database. We will use symmetric encryption (like Fernet from the Cryptography library, which is built on AES-128 in CBC mode with HMAC for authenticity). Every credential’s sensitive data will be encrypted using a master key, ensuring that even if the database is compromised, the actual tokens/keys are not readable without the decryption key.

Master Encryption Key: We generate a random key (using Fernet.generate_key() or similar) and store it securely outside the database (e.g., as an environment variable or in a secrets manager). This key must remain secret and not be hard-coded in code or in the DB. In practice, one might load it via an environment variable or a config file. For example, one could base64-encode the key to store in an env var. A developer article notes that Fernet is easy to use and strong, but the secret key must be kept out of code and loaded securely (e.g. from dotenv or environment) ￼. In other words, never commit the key; keep it in config and perhaps even double-encode it (like base64) so that an accidental log won’t directly reveal it ￼.

Encryption/Decryption Utilities: We will create small utility functions to handle encryption and decryption of credential data using this master key. For example:

```python
from cryptography.fernet import Fernet

# Assume `FERNET_KEY` is our base64-encoded key from env
fernet = Fernet(FERNET_KEY)

def encrypt_payload(plaintext: bytes) -> bytes:
    return fernet.encrypt(plaintext)

def decrypt_payload(token: bytes) -> bytes:
    return fernet.decrypt(token)
```

We can use these to encrypt the credential details before saving to the DB, and to decrypt when we need to use them. Typically, we’ll serialize the credential fields into a JSON string, then encrypt that string. For example, if a user provides a new GitHub PAT credential with token “abcd…”, we might do:

```
data = {"token": "abcd1234..."}              # dict of secret fields
plaintext = json.dumps(data).encode("utf-8") # serialize to bytes
ciphertext = encrypt_payload(plaintext)      # encrypt with Fernet
```

The resulting ciphertext (which is a bytes value containing the encrypted data) is what we store in the database. (It can be stored in a BYTEA column or base64-encoded into a text column if needed.)

This design mirrors n8n’s security approach: n8n also encrypts all stored credential data using an encryption key ￼. The encryption ensures that credential values cannot be read or manipulated without the master key. In our system, whenever credentials are accessed, the backend will decrypt them in memory for use, but it will never send decrypted secrets to the client or store them in plaintext.

We also leverage Pydantic’s SecretStr/SecretBytes for handling these values in memory safely. These types avoid printing the actual secret (they display as "********" when converted to string). This is a helpful precaution for logging or error messages – for instance, if an API returns credential info, it should not accidentally reveal the token. The SecretStr values can be obtained via .get_secret_value() when actually needed for encryption or usage ￼. This, combined with encryption at rest, creates a strong security posture:

* At rest: data is encrypted with a key not stored in the DB.
* In transit: the API will transmit secrets only when absolutely necessary (ideally never to clients; clients send secrets to create credentials, which the server encrypts).
* In memory: use secret types or careful handling to avoid leaks in logs.

## Credential Database Model

We will use PostgreSQL to store credentials, with SQLAlchemy (or an ORM of choice) to model the table. A single Credentials table can hold all types of credentials, since the actual fields differ by type and we plan to store the encrypted blob of data. The model might look like:

```
from sqlalchemy import Column, Integer, String, LargeBinary, Boolean, ForeignKey

class CredentialDB(SQLAlchemyBase):
    __tablename__ = "credentials"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)        # user-defined name for the credential
    type = Column(String, nullable=False)        # e.g. "github_pat", "ssh_key"
    encrypted_data = Column(LargeBinary, nullable=False)  # encrypted blob of all secret fields
    owner_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_shared = Column(Boolean, default=False)   # whether this credential is shared/reusable
    # Optionally: fields for team sharing, e.g. owner_team_id, etc.
```

Name: Each credential has a user-defined name (like “My GitHub Token”) to identify it. This is what users will reference when choosing a credential for a plugin. Names are unique per user or per team scope.

Type: The type string corresponds to the credential class/registry key (e.g. “github_pat”). This tells us how to interpret the encrypted data (which fields are inside).

Encrypted_data: This holds the output from encrypt_payload() – essentially a ciphertext that encapsulates all the sensitive fields for this credential. We treat this as an opaque binary (or base64 text). Only the application (with the master key) can decrypt and get the actual fields.

Owner and Sharing: We include owner_user_id to record who created/owns the credential. The is_shared flag is a simplification to indicate if a credential is shared beyond the owner. For more fine-grained sharing, we might have a separate join table like credential_shares that lists which user or team IDs have access. But a basic approach is:
* If is_shared is false: only the owner can use it.
* If is_shared is true: any user in the same organization/team (or perhaps any user, depending on context) can use it. In a multi-tenant environment, you’d likely limit sharing to specific users or teams. For team-based sharing, a team_id column or a mapping table would be used.

In n8n, for instance, you can share a credential with specific users or projects, and those users can use the credential but cannot see its contents ￼. Our design can accommodate that: the UI/API would allow the owner to mark a credential as shared with certain users/teams, and those associations would be stored (with the rule that non-owners retrieving the credential via API can only see metadata, not the decrypted secret). The database model can be extended with a join table (credential_id, shared_with_user_id or shared_with_team_id) to list authorized access, if needed.

Reusability: By default, credentials are reusable in the sense that a single stored credential can be referenced by multiple plugins or integrations. If the user updates that credential (e.g. updates the token), all plugins using it will effectively use the new value. We may mark some credentials as non-reusable (perhaps if we wanted to tie them to a single plugin), but generally tagging as reusable just means it’s available to select in any plugin config that needs that type of credential.

## API Endpoints for Credential Management

We will expose a set of FastAPI endpoints to manage credentials. These allow clients (and future UI frontends) to create and use credentials via the defined schemas. For example:
* List Credential Types: GET /credential-types – returns a list of available credential types and their schema definitions (fields, labels, etc.). This helps the UI know what types can be created and how to render the form for each.
* Create Credential: POST /credentials – create a new credential. The request would include a type (credential type key), a name, and the required fields (with their values). The server will:
	1.	Validate the input fields against the schema for that type (e.g. ensure required fields are present, data types are correct).
	2.	Encrypt the sensitive data payload with the master key.
	3.	Save a new record in the Credentials table with the provided name, type, owner, and the encrypted blob.
	4.	Return a success response (often the credential metadata, sans secrets).
* List Credentials: GET /credentials – list credentials available to the requesting user. This will show each credential’s id, name, type, maybe owner (if admin) or shared info, etc., but not the secret values. For instance:

```json
[
  {"id": 1, "name": "My GitHub Token", "type": "github_pat", "shared": false},
  {"id": 2, "name": "Team SSH Key", "type": "ssh_key", "shared": true}
]
```

The client can use this list to show what credentials the user has or can use.

* Get Credential Details: GET /credentials/{id} – returns details for a single credential. For security, this would typically return the same data as list (no secrets), or possibly include decrypted fields only if it’s being accessed in a secure context (though usually you wouldn’t send secrets back to the UI once created; the UI should treat the stored credential as a black box after creation).
* Delete Credential: DELETE /credentials/{id} – remove a credential (if not in use or if user wants to revoke it).
* Update Credential: PUT /credentials/{id} – update the fields or metadata of a credential. If updating secret fields, the new values should be encrypted again before storing.

During creation, because we have dynamic fields, the payload could be something like:

```
{
  "type": "github_pat",
  "name": "My GitHub Token",
  "fields": {
    "token": "ghp_abcd1234..." 
  }
}
```

The API handler will lookup the schema for github_pat via the registry, validate that "token" is provided and is a string, then encrypt the {"token": "ghp_abcd..."} object. Important: The encryption should happen server-side, and the raw token should not be stored or logged. Only the encrypted result is saved ￼.

We also ensure that the master key is never exposed via the API. The server holds it in memory (from env) to do encryption/decryption but never transmits it.

For retrieving credentials: Typically, the UI or client does not need the actual secret value; they just need to select a credential by name/ID to use it in some operation. So our API might not ever send back the plaintext secret after creation (except perhaps for display immediately after creation if we allow viewing it once). This is similar to other systems: e.g., in n8n, when you use a credential, you choose it by name in a node; you cannot directly view the credential’s secret once stored (non-owners especially cannot) ￼. We might allow the owner to fetch and decrypt their own credential (to remind themselves of the token) via a secure endpoint, but that’s optional and would be carefully protected.

Example: A FastAPI route using the Pydantic model approach could look like:

```python
from fastapi import APIRouter, HTTPException, Depends
router = APIRouter()

@router.get("/credential-types")
def list_types():
    # Return all types and their field schemas for UI
    types = []
    for type_name, cls in credential_registry.items():
        types.append({
            "type": type_name,
            "display_name": cls.display_name,
            "fields": cls.fields  # or generate Pydantic schema
        })
    return types

@router.post("/credentials")
def create_credential(payload: CreateCredentialRequest, user=Depends(current_user)):
    # payload might have .type, .name, .fields (as a dict)
    cred_type = payload.type
    if cred_type not in credential_registry:
        raise HTTPException(400, detail="Unknown credential type")
    schema = credential_registry[cred_type].fields
    # Validate payload.fields keys and types against schema...
    # (This could use Pydantic model for that type to validate easily)
    # Encrypt the fields
    plaintext = json.dumps(payload.fields).encode('utf-8')
    ciphertext = encrypt_payload(plaintext)
    # Store in DB
    cred = CredentialDB(
        name=payload.name,
        type=cred_type,
        encrypted_data=ciphertext,
        owner_user_id=user.id,
        is_shared=payload.shared or False
    )
    db_session.add(cred)
    db_session.commit()
    return {"id": cred.id, "name": cred.name, "type": cred.type, "shared": cred.is_shared}
```

This illustrates the flow: validate input -> encrypt -> store -> return metadata.


## Using Credentials in Plugin Registration Flow

One of the main uses of this credential system is to supply secrets to the plugin registration and usage flow. For instance, if the platform allows users to register a plugin by providing a Git repository URL for the plugin’s code, and that repository is private, the user should attach a credential (GitHub token, GitLab token, or SSH key) so the system can access the repo.

The plugin registration might be another API like POST /plugins with data: e.g. {"name": "MyPlugin", "repo_url": "...", "credential_id": 1}. Here credential_id corresponds to a stored credential that has access to that repo. The system will then:
	1.	Lookup Credential: Retrieve the credential record by ID. Ensure the requesting user has access to it (either they own it or it’s shared with them).
	2.	Decrypt the Credential: Use the master key to decrypt the encrypted_data. This yields the original fields (e.g., {"token": "ghp_abcdef..."} or an SSH key).
	3.	Use Credential for Access: Depending on the type, the system will apply the credential to perform the needed action. For Git cloning:
* If it’s a GitHub/GitLab PAT, the system can perform a Git clone over HTTPS using the token. For example, construct an authenticated URL: https://<token>@github.com/owner/repo.git. The token can be placed in the URL or provided via a Git credential helper or using an HTTP header. (For one-time clone, embedding in the URL is straightforward).
* If it’s a GitLab OAuth token, similarly use it as a Bearer token for API access or in the URL for Git if supported.
* If it’s an SSH key, the system needs to perform a Git clone over SSH. This involves making the private key available to the git command. One method is to write the key to a temporary file and use the GIT_SSH_COMMAND environment variable to specify using that key (e.g., GIT_SSH_COMMAND="ssh -i /tmp/tempkey" when running git clone git@github.com:owner/repo.git). Another method is to use an SSH library or agent. The system can handle this internally; the important part is it uses the decrypted key content. If a passphrase is needed, it might use sshpass or a similar approach, but generally using keys without passphrase or prompting the user to ensure it’s unencrypted might be simpler for automation.
	4.	Plugin Installation: With the repository access granted by the credential, the system can clone or pull the repository’s content to install the plugin.

The credential classes can assist in this usage. For example, each credential type class could have a method like apply(auth_context) or similar. But a simpler approach is just to handle it procedurally:

```python
cred = get_credential(id=credential_id)
fields = json.loads(decrypt_payload(cred.encrypted_data))
if cred.type == "github_pat":
    token = fields["token"]
    # Use token in clone URL or set HTTP header for git if using a library
    repo_url = insert_token_into_url(cred_repo_url, token) 
    git("clone", repo_url, ...)
elif cred.type == "ssh_key":
    key = fields["private_key"]; passphrase = fields.get("passphrase")
    write_temp_file("key.pem", key)
    # e.g., use subprocess to call git with GIT_SSH_COMMAND
    os.environ["GIT_SSH_COMMAND"] = f'ssh -i {temp_key_path} -o StrictHostKeyChecking=no'
    git("clone", ssh_repo_url, ...)
```

This is pseudocode, but demonstrates how the system injects the credential. The important aspect is that the plugin registry explicitly references a credential rather than the user providing raw secrets each time. This decoupling means credentials are centrally managed and updated. If the token expires or rotates, the user can update the credential in one place, and the plugin can re-use it.

Another benefit is security and auditing: since the system knows exactly which credential is used for which plugin, it can log usage or restrict certain credentials to certain actions.

## Credential Sharing and Reusability

Our design allows credentials to be shared between users or within teams to facilitate collaboration, similar to n8n’s credential sharing features. Credential sharing means one user can allow others to use a credential without revealing the secret value to them ￼.

User/Team Sharing: If using a multi-tenant or collaborative platform, a credential could be associated with a team or project. For example, a team might have a “Shared GitLab Token” credential that all members can use for various plugins. In our database model, we included a boolean is_shared as a basic indicator, but a more complete implementation might involve a separate mapping:
* A table credential_access with columns credential_id and user_id (or team_id), granting access rights. The owner can add entries here for other users or an entire team.
* When listing credentials for a user, include those they own plus those shared with them.
* When using a credential, check that the user (or their team) is either the owner or is listed in the access table.

Crucially, even if a credential is shared, only the system ever decrypts it. Other users cannot retrieve the plaintext secret via the API. They can only select the credential by name/ID to use in a plugin. This way, a team member can, say, trigger a workflow that uses a shared AWS key credential without ever seeing the actual key. This follows the principle of least privilege and prevents unnecessary exposure of secrets.

Reusable Credentials: By default, credentials in this system are reusable – you create one and then you can attach it to multiple plugins or tasks. We might allow tagging or categorizing credentials for clarity (e.g., marking some as “Reusable” or grouping by project). In practice, “reusable” just means it’s not tied to a single plugin. For example, a user might create one “GitHub PAT” credential and use it for several plugin registrations (maybe multiple private repos). If the user leaves an organization, an admin could transfer or update those credentials rather than having multiple duplicate tokens.

We also ensure that updating a credential (e.g., providing a new token value) will immediately affect all plugins that reference it. This is beneficial for token rotation scenarios – update the token in one place instead of editing every plugin config.

Permission-wise, only the credential’s owner (or an admin) should be able to edit or delete it. Shared users can use but not modify someone else’s credential ￼. This prevents accidental changes and maintains trust.

## Example Implementation Snippets

Below are some simplified code snippets to illustrate how parts of this system could be implemented:

1. Credential Type Definitions and Registry:

```python
# Base class and registry
credential_registry = {}

class BaseCredentialType:
    type_name: str
    display_name: str
    fields: list  # list of field schema dicts

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if getattr(cls, "type_name", None):
            credential_registry[cls.type_name] = cls

# Concrete credential types
class GithubPATCred(BaseCredentialType):
    type_name = "github_pat"
    display_name = "GitHub Personal Access Token"
    fields = github_pat_fields

class GitlabPATCred(BaseCredentialType):
    type_name = "gitlab_pat"
    display_name = "GitLab Personal Access Token"
    fields = gitlab_pat_fields

class SSHKeyCred(BaseCredentialType):
    type_name = "ssh_key"
    display_name = "SSH Key"
    fields = ssh_key_fields

# Now credential_registry = {
#   "github_pat": GithubPATCred,
#   "gitlab_pat": GitlabPATCred,
#   "ssh_key": SSHKeyCred
# }
```

Each class specifies its fields which were defined earlier. We can easily iterate credential_registry to get all available types and their schemas for an endpoint or documentation.

2. Encryption Utilities (using Fernet):

```python
from cryptography.fernet import Fernet

# Load the master key (e.g., from env variable MASTER_KEY which is base64 encoded)
MASTER_KEY = os.environ["MASTER_KEY"]  # This would be a base64url string from Fernet.generate_key()
fernet = Fernet(MASTER_KEY.encode())

def encrypt_value(value: bytes) -> bytes:
    return fernet.encrypt(value)

def decrypt_value(token: bytes) -> bytes:
    return fernet.decrypt(token)
```

This uses a single Fernet key for all credentials. As noted, the key must remain secret and not be hard-coded – one should inject it via configuration and keep it out of source control ￼. Optionally, we could incorporate key rotation in the future (Fernet supports rotating keys by maintaining multiple keys and tagging ciphertext with key info ￼, but to keep it simple, we start with one key).

3. SQLAlchemy Model (CredentialDB) and Pydantic Model (Credential):

```python
# SQLAlchemy model (as defined earlier)
class CredentialDB(Base):
    __tablename__ = "credentials"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    encrypted_data = Column(LargeBinary, nullable=False)
    owner_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_shared = Column(Boolean, default=False)
    # ...

# Pydantic model for returning credential info (non-sensitive)
from pydantic import BaseModel
class CredentialInfo(BaseModel):
    id: int
    name: str
    type: str
    shared: bool

```

We use CredentialInfo as the schema for responses so that we never accidentally serialize the encrypted data or plaintext. This model only includes metadata.

4. FastAPI Endpoint Example (Create Credential):

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter()

class CreateCredentialRequest(BaseModel):
    type: str
    name: str
    fields: dict  # dynamic fields for the credential

@router.post("/credentials", response_model=CredentialInfo)
def create_credential(req: CreateCredentialRequest, current_user: User = Depends(get_current_user)):
    # 1. Check type validity
    cred_class = credential_registry.get(req.type)
    if not cred_class:
        raise HTTPException(status_code=400, detail="Unsupported credential type.")
    # 2. Validate fields (using Pydantic model if available)
    try:
        if req.type == "github_pat":
            GithubPATModel(**req.fields)      # will raise if fields invalid
        elif req.type == "gitlab_pat":
            GitlabPATModel(**req.fields)
        elif req.type == "ssh_key":
            SSHKeyModel(**req.fields)
        # else, for other types, could dynamically validate...
    except Exception as e:
        raise HTTPException(status_code=422, detail="Invalid credential fields: " + str(e))
    # 3. Encrypt the fields
    plaintext = json.dumps(req.fields).encode()
    ciphertext = encrypt_value(plaintext)
    # 4. Store in DB
    cred_db = CredentialDB(
        name=req.name,
        type=req.type,
        encrypted_data=ciphertext,
        owner_user_id=current_user.id,
        is_shared=False
    )
    session.add(cred_db)
    session.commit()
    return CredentialInfo(id=cred_db.id, name=cred_db.name, type=cred_db.type, shared=cred_db.is_shared)
```

This is a simplified example. In practice, you might abstract some of this logic (for instance, use the registry class to obtain a Pydantic validator or use a generic validation mechanism). But it shows the core steps: validate input, encrypt it, save, return non-sensitive info.

5. Using Credential in Plugin Operation:

Let’s say we have a function to clone a git repo for a plugin:

```python

import subprocess, tempfile

def clone_repo(repo_url: str, cred_id: int):
    # Get credential
    cred = session.query(CredentialDB).get(cred_id)
    if not cred:
        raise Exception("Credential not found")
    # Check access rights (e.g., current_user can access cred)
    if cred.owner_user_id != current_user.id and not is_credential_shared_with(cred, current_user):
        raise Exception("No access to this credential")

    # Decrypt credentials
    fields = json.loads(decrypt_value(cred.encrypted_data))
    # Use based on type
    if cred.type in ("github_pat", "gitlab_pat"):
        token = fields["token"]
        # For HTTPS URL: embed token (note: URL-encode token if necessary)
        # e.g., repo_url = "https://github.com/org/name.git"
        auth_url = repo_url.replace("https://", f"https://{token}@")
        subprocess.run(["git", "clone", auth_url, "/plugins/LocalPath"], check=True)
    elif cred.type == "ssh_key":
        private_key = fields["private_key"]
        passphrase = fields.get("passphrase")
        # Write key to temp file
        key_file = tempfile.NamedTemporaryFile(delete=False)
        key_file.write(private_key.encode())
        key_file.close()
        # Use SSH command with this key
        ssh_cmd = f"ssh -i {key_file.name} -o StrictHostKeyChecking=no"
        env = os.environ.copy()
        env["GIT_SSH_COMMAND"] = ssh_cmd
        subprocess.run(["git", "clone", repo_url, "/plugins/LocalPath"], check=True, env=env)
        # Clean up temp key file if needed
```


In this pseudo-code, for PAT-based credentials we simply inject the token into the clone URL (Git will use it as an HTTP Basic auth password). For SSH, we write the key and tell Git to use it. This is one straightforward approach; alternatives include using libraries or an SSH agent. The key point is that the system retrieves and uses the secret at runtime without exposing it elsewhere.

Notice we must handle the case where the credential is not accessible by the user. If a user tries to use a credential they don’t own and which isn’t shared with them, we should forbid it. This check happens before decryption/usage.

Additionally, in a real scenario, after cloning, the plugin code might be loaded, etc. Our focus here is just how the credential feeds into that process.

Conclusion

The proposed design provides a secure, flexible, and extensible credential management system for a FastAPI platform:
* It uses a registry of credential types to support dynamic form generation and easy extension (new types can be added with minimal effort).
* JSON-schema-like field definitions (or Pydantic models) describe each credential’s required inputs (labels, types, help text), enabling an n8n-like UI where forms adjust to the chosen credential type ￼.
* All sensitive data is encrypted at rest using industry-standard cryptography (Fernet/AES). A master key (stored outside the DB) is used to encrypt/decrypt, ensuring that credential secrets in the DB are not stored in plaintext ￼ ￼.
* The system cleanly separates credential storage from usage: plugins reference credentials by name/ID, and the actual secret is fetched and injected server-side only when needed. This keeps configuration simple for users and maintains security.
* Sharing and reuse features allow teams to collaboratively use credentials without exposing secrets to every user ￼. Credentials can be marked as shared or linked to multiple users, and can be reused across multiple plugins, reducing duplication.
* By following these practices, the system remains easy to reason about: each credential is a self-contained object with known fields and secure handling. The design is similar to n8n’s credentials (which are defined with properties and encrypted for storage) ￼, making it suitable for building a UI that lists credential types, lets users create/edit them, and select them for use in various integrations.

Overall, this approach provides a robust foundation for credential management in a modern FastAPI application, balancing security, extensibility, and user-friendliness. By using structured schemas and strong encryption, we ensure that adding new credential types or new integrations can be done safely and with minimal friction.
