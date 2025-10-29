# 🗄️ Storage Provider Evaluation - Sietch Faces

**Created:** October 29, 2025  
**Status:** 🟡 Awaiting Approval  
**Purpose:** Evaluate storage options for uploaded user images in the CORE service

---

## 📋 Executive Summary

This document evaluates three storage options for handling uploaded user images in the Sietch Faces platform:

1. **Cloudflare R2** ⭐ **(RECOMMENDED)**
2. **Amazon S3**
3. **Google Drive** (User-owned storage)

**Key Recommendation:** Start with **Cloudflare R2** due to:
- Zero egress fees (critical for image-heavy app)
- Better free tier than S3
- S3-compatible API (easy migration if needed)
- Lower operational costs at scale

---

## 🎯 Requirements Analysis

### Current System
- **Storage Method:** Local filesystem (`uploads/` directory)
- **File Types:** Images (JPEG, PNG)
- **Current Usage:** Development/testing only
- **Access Pattern:** Frequent reads (photo viewing), infrequent writes (uploads)

### Production Requirements
1. **Scalability:** Handle growing image library (thousands to millions of images)
2. **Reliability:** 99.9%+ uptime, data durability
3. **Performance:** Fast image serving for web and mobile clients
4. **Cost-Effective:** Minimize storage and bandwidth costs
5. **Security:** Private image storage with access controls
6. **API Integration:** Easy to integrate with FastAPI/Next.js
7. **Migration Path:** Ability to migrate to different provider if needed

---

## 🔍 Option 1: Cloudflare R2 ⭐ (RECOMMENDED)

### Overview
Cloudflare R2 is an S3-compatible object storage service with zero egress fees.

### ✅ Advantages

#### Cost Structure
- **Storage:** $0.015/GB/month (same as S3 Standard)
- **Class A Operations (writes):** $4.50 per million requests
- **Class B Operations (reads):** $0.36 per million requests
- **Egress:** **$0** (FREE) - This is the killer feature! 🎯
- **Ingress:** FREE

#### Free Tier
- **10 GB/month** storage (included forever)
- **1 million Class A operations/month**
- **10 million Class B operations/month**

**Why This Matters:**
For an image-heavy application like Sietch Faces, egress (data transfer out) is typically the largest cost. R2 eliminates this entirely.

#### Technical Features
- ✅ **S3-Compatible API** - Use existing S3 SDKs and tools
- ✅ **Global CDN Integration** - Built-in Cloudflare CDN
- ✅ **Fast Performance** - Cloudflare's global network
- ✅ **Automatic Backups** - Data replicated across locations
- ✅ **Public/Private Buckets** - Flexible access control
- ✅ **Custom Domains** - Serve images from your domain
- ✅ **Image Transformations** - Cloudflare Images integration (optional)

#### Integration Ease
- **Python SDK:** boto3 (same as S3)
- **JavaScript SDK:** @aws-sdk/client-s3
- **Migration:** Simple switch from S3 if needed (just change endpoint)

#### Example Code
```python
# Python (boto3)
import boto3

s3 = boto3.client(
    's3',
    endpoint_url='https://<account_id>.r2.cloudflarestorage.com',
    aws_access_key_id='<access_key>',
    aws_secret_access_key='<secret_key>',
    region_name='auto'
)

# Upload image
s3.upload_file('photo.jpg', 'sietch-faces-images', 'uploads/uuid.jpg')

# Generate presigned URL (temporary access)
url = s3.generate_presigned_url(
    'get_object',
    Params={'Bucket': 'sietch-faces-images', 'Key': 'uploads/uuid.jpg'},
    ExpiresIn=3600  # 1 hour
)
```

### ❌ Considerations
- Newer service (since 2022) - less battle-tested than S3
- Requires Cloudflare account
- Limited advanced features compared to S3 (but improving)
- No built-in ML/AI services like AWS Rekognition

### Cost Estimate (Production)
**Scenario:** 1,000 users, 10 photos each, 2MB average size

| Item | Calculation | Monthly Cost |
|------|-------------|--------------|
| Storage | 20 GB × $0.015 | $0.30 |
| Uploads | 10K photos × $4.50/million | $0.05 |
| Views | 100K views × $0.36/million | $0.04 |
| Egress | Unlimited | **$0.00** |
| **Total** | | **$0.39/month** |

**With S3, same scenario:**
- Storage: $0.46
- Uploads: $0.05
- Egress (100K views × 2MB = 200GB): **$18.00** ⚠️
- **Total: ~$18.50/month**

**Savings: ~$18/month or 97% less! 🎉**

---

## 🔍 Option 2: Amazon S3

### Overview
Industry-standard object storage, widely used and battle-tested.

### ✅ Advantages

#### Maturity & Reliability
- ✅ **Battle-Tested** - Running since 2006
- ✅ **99.999999999% Durability** (11 nines)
- ✅ **99.9% Availability SLA**
- ✅ **Extensive Documentation** - Huge community

#### Technical Features
- ✅ **Storage Classes** - Standard, IA, Glacier for cost optimization
- ✅ **Lifecycle Policies** - Auto-archive old images
- ✅ **Versioning** - Keep image history
- ✅ **Access Control** - Fine-grained IAM policies
- ✅ **Event Notifications** - Trigger functions on upload
- ✅ **CloudFront CDN** - Fast global delivery
- ✅ **AWS Rekognition** - Built-in ML for face detection

#### Integration
- **Ecosystem:** Best AWS integration (Lambda, API Gateway, etc.)
- **SDKs:** Mature SDKs for all languages
- **Tools:** AWS CLI, GUI clients, etc.

### ❌ Disadvantages
- **Egress Costs:** $0.09/GB for first 10TB ⚠️
- **Complexity:** More options = more decisions
- **Vendor Lock-in:** Harder to migrate once using AWS services
- **Free Tier:** Only 5GB for 12 months (then expires)

### Cost Estimate (Production)
Same scenario as above (1,000 users, 10 photos each, 2MB average):

| Item | Calculation | Monthly Cost |
|------|-------------|--------------|
| Storage | 20 GB × $0.023 | $0.46 |
| PUT requests | 10K × $0.005/1000 | $0.05 |
| GET requests | 100K × $0.0004/1000 | $0.04 |
| Egress | 200 GB × $0.09 | **$18.00** ⚠️ |
| **Total** | | **$18.55/month** |

**Note:** Costs scale significantly with user growth due to egress fees.

### When to Choose S3
- Already using AWS ecosystem heavily
- Need advanced features (Glacier, Rekognition, etc.)
- Require mature disaster recovery features
- Have AWS credits or enterprise agreements

---

## 🔍 Option 3: Google Drive (User-Owned Storage)

### Overview
Allow users to store their photos in their own Google Drive, giving them full ownership.

### ✅ Advantages

#### User Benefits
- ✅ **User Ownership** - Photos stay in user's Google Drive
- ✅ **No Storage Costs** - Users use their own storage quota
- ✅ **Privacy** - Users control their data
- ✅ **Familiar Interface** - Can access via Drive app
- ✅ **Backup** - Google handles backups

#### Business Benefits
- ✅ **Zero Storage Costs** - No need to pay for storage
- ✅ **Reduced Liability** - Users own their data
- ✅ **Scalability** - Infinite scale at no cost

### ❌ Disadvantages

#### Technical Challenges
- ❌ **API Complexity** - Google Drive API is more complex than S3
- ❌ **OAuth Flow** - Requires user authorization
- ❌ **Rate Limits** - Per-user quotas (10,000 requests/day)
- ❌ **Performance** - Slower than dedicated object storage
- ❌ **Reliability** - Depends on user's Drive quota
- ❌ **Privacy Concerns** - App needs Drive access

#### Implementation Complexity
```python
# Requires OAuth2 flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# 1. User authorizes app (OAuth2)
# 2. App gets access token
# 3. Upload to user's Drive
service = build('drive', 'v3', credentials=creds)
file_metadata = {'name': 'photo.jpg', 'parents': ['folder_id']}
media = MediaFileUpload('photo.jpg', mimetype='image/jpeg')
file = service.files().create(
    body=file_metadata,
    media_body=media,
    fields='id'
).execute()
```

#### User Experience Issues
- Users must grant Drive access (friction)
- Users can delete/move files (breaking references)
- Different users have different quota limits
- Offline access complicated
- Sharing between users complex

### Recommendation for Google Drive
**Not recommended as primary storage**, but consider as:
- **Optional feature:** "Backup to Google Drive"
- **Export feature:** "Download all my photos to Drive"
- **Hybrid approach:** Store in R2, sync to Drive as backup

---

## 📊 Comparison Matrix

| Feature | Cloudflare R2 ⭐ | Amazon S3 | Google Drive |
|---------|-----------------|-----------|--------------|
| **Storage Cost** | $0.015/GB | $0.023/GB | FREE (user-owned) |
| **Egress Cost** | **FREE** 🎉 | $0.09/GB ⚠️ | FREE |
| **Free Tier** | 10GB forever | 5GB for 12mo | 15GB (user quota) |
| **API Complexity** | Simple (S3-compatible) | Simple | Complex (OAuth) |
| **Performance** | Excellent | Excellent | Good |
| **Reliability** | High | Very High | Medium |
| **Setup Time** | 1-2 hours | 1-2 hours | 1-2 days |
| **Migration Risk** | Low (S3-compatible) | Medium | High |
| **User Control** | None | None | Full |
| **Privacy** | App-controlled | App-controlled | User-controlled |
| **Best For** | Cost-effective production | AWS ecosystem | Optional backup |

---

## 🎯 Recommendation

### Primary Storage: **Cloudflare R2** ⭐

**Rationale:**
1. **Cost-Effective:** 97% cheaper than S3 for our use case
2. **Simple:** S3-compatible API = easy development
3. **Fast:** Cloudflare's global CDN
4. **Scalable:** Handles millions of images
5. **Flexible:** Can migrate to S3 if needed (just change endpoint)

### Implementation Plan

#### Phase 1: R2 Integration (Recommended First)
1. Create Cloudflare account and R2 bucket
2. Add boto3 dependency
3. Create storage service abstraction layer
4. Update upload route to use R2
5. Implement presigned URLs for private access
6. Test upload/download flows
7. Update configuration/environment variables
8. Document setup process

**Estimated Time:** 1-2 days

#### Phase 2: Optional Google Drive Export (Future Enhancement)
1. Implement "Export to Google Drive" feature
2. Allow users to backup their entire library
3. OAuth flow for Drive authorization
4. Batch export with progress tracking

**Estimated Time:** 3-5 days (lower priority)

---

## 🔧 Technical Implementation Details

### Storage Service Abstraction

Create an abstraction layer to allow easy switching between providers:

```python
# app/storage/base.py
from abc import ABC, abstractmethod

class StorageProvider(ABC):
    @abstractmethod
    def upload(self, file_path: str, key: str) -> str:
        """Upload file and return URL"""
        pass
    
    @abstractmethod
    def download(self, key: str, dest_path: str) -> None:
        """Download file to local path"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete file"""
        pass
    
    @abstractmethod
    def generate_presigned_url(self, key: str, expires_in: int) -> str:
        """Generate temporary access URL"""
        pass

# app/storage/r2.py
class R2StorageProvider(StorageProvider):
    def __init__(self):
        self.client = boto3.client(
            's3',
            endpoint_url=settings.r2_endpoint,
            aws_access_key_id=settings.r2_access_key,
            aws_secret_access_key=settings.r2_secret_key,
            region_name='auto'
        )
        self.bucket = settings.r2_bucket
    
    def upload(self, file_path: str, key: str) -> str:
        self.client.upload_file(file_path, self.bucket, key)
        return f"https://{self.bucket}.r2.dev/{key}"
    
    # ... implement other methods

# app/storage/factory.py
def get_storage_provider() -> StorageProvider:
    provider = settings.storage_provider  # "r2", "s3", "local"
    if provider == "r2":
        return R2StorageProvider()
    elif provider == "s3":
        return S3StorageProvider()
    else:
        return LocalStorageProvider()
```

### Configuration Updates

```python
# app/config.py additions
class Settings(BaseSettings):
    # ... existing settings ...
    
    # Storage Provider
    storage_provider: str = "local"  # "local", "r2", "s3"
    
    # Cloudflare R2 Settings
    r2_account_id: str = ""
    r2_access_key: str = ""
    r2_secret_key: str = ""
    r2_bucket: str = "sietch-faces-images"
    r2_endpoint: str = ""  # Computed from account_id
    r2_public_url: str = ""  # Custom domain if configured
    
    # Amazon S3 Settings (if needed)
    s3_bucket: str = ""
    s3_region: str = "us-east-1"
    s3_access_key: str = ""
    s3_secret_key: str = ""
    
    @property
    def r2_endpoint_url(self) -> str:
        if self.r2_account_id:
            return f"https://{self.r2_account_id}.r2.cloudflarestorage.com"
        return ""
```

### Environment Variables

```bash
# .env additions

# Storage Provider Selection
STORAGE_PROVIDER=r2  # Options: local, r2, s3

# Cloudflare R2 Configuration
R2_ACCOUNT_ID=your_account_id
R2_ACCESS_KEY=your_access_key
R2_SECRET_KEY=your_secret_key
R2_BUCKET=sietch-faces-images
R2_PUBLIC_URL=https://images.sietch-faces.com  # Optional custom domain
```

### Dependencies Update

```txt
# requirements.txt additions
boto3>=1.28.0  # For R2/S3 integration
```

---

## 🚀 Migration Strategy

### From Local to R2

**Option 1: Big Bang Migration**
1. Upload all existing files to R2
2. Update database paths
3. Switch config to R2
4. Delete local files

**Option 2: Gradual Migration**
1. New uploads go to R2
2. Keep old files local
3. Lazy migration: move to R2 on first access
4. Background job: migrate all files over time

**Recommended:** Option 2 for production, Option 1 for development

### From R2 to S3 (if needed)

Since R2 is S3-compatible:
1. Update endpoint URL
2. Update credentials
3. Sync buckets using AWS CLI or rclone
4. Switch config

**Downtime:** Minimal (can run both during migration)

---

## 🔐 Security Considerations

### R2 Security Best Practices
1. **Private Buckets** - Never make bucket public
2. **Presigned URLs** - Use temporary URLs for access
3. **IAM Policies** - Least privilege access
4. **Encryption** - Enable at-rest encryption
5. **Access Logs** - Monitor access patterns
6. **CORS** - Configure for frontend access

### Access Control Pattern
```python
# Generate presigned URL for private image access
def get_image_url(image_key: str, user_id: str) -> str:
    # 1. Verify user has permission to access this image
    if not user_has_permission(user_id, image_key):
        raise HTTPException(403, "Access denied")
    
    # 2. Generate temporary URL (expires in 1 hour)
    storage = get_storage_provider()
    url = storage.generate_presigned_url(image_key, expires_in=3600)
    
    return url
```

---

## 📈 Scalability Analysis

### Growth Scenarios

**Year 1: 1,000 users**
- Storage: 20 GB
- Monthly cost (R2): ~$0.39
- Monthly cost (S3): ~$18.55

**Year 2: 10,000 users**
- Storage: 200 GB
- Monthly cost (R2): ~$3.90
- Monthly cost (S3): ~$185.50

**Year 3: 100,000 users**
- Storage: 2 TB
- Monthly cost (R2): ~$39
- Monthly cost (S3): ~$1,855

**5-Year Savings with R2: ~$10,000+ 💰**

---

## 🎓 Learning Resources

### Cloudflare R2
- [Official Documentation](https://developers.cloudflare.com/r2/)
- [R2 vs S3 Comparison](https://developers.cloudflare.com/r2/platform/s3-compatibility/)
- [boto3 with R2](https://developers.cloudflare.com/r2/examples/boto3/)

### Amazon S3
- [S3 Getting Started](https://docs.aws.amazon.com/s3/)
- [boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

### Google Drive API
- [Drive API Overview](https://developers.google.com/drive/api/guides/about-sdk)
- [Python Quickstart](https://developers.google.com/drive/api/quickstart/python)

---

## ✅ Decision Checklist

Before implementation, confirm:

- [ ] **Budget Approved:** Development team has approval for R2 costs
- [ ] **Cloudflare Account:** Account created with payment method
- [ ] **R2 Bucket Created:** Bucket provisioned and configured
- [ ] **Credentials Generated:** Access keys created and secured
- [ ] **Security Review:** Access policies reviewed
- [ ] **Backup Strategy:** Backup plan documented
- [ ] **Migration Plan:** Strategy for moving existing files (if any)
- [ ] **Documentation Updated:** Setup docs include R2 configuration

---

## 🎯 Next Steps

### Awaiting Approval ✋

Please review this evaluation and confirm:

1. **Approval for R2:** Can we proceed with Cloudflare R2 as primary storage?
2. **Budget Confirmation:** Cloudflare account setup approved?
3. **Google Drive Priority:** Should Google Drive export be included in Phase 1 or deferred?

### Once Approved, Implementation Order:

1. **Setup R2 Account** (30 minutes)
2. **Create Storage Abstraction** (2-3 hours)
3. **Update Configuration** (1 hour)
4. **Modify Upload Route** (2-3 hours)
5. **Add Presigned URL Support** (1-2 hours)
6. **Testing** (2-3 hours)
7. **Documentation** (1 hour)
8. **Deploy to Staging** (1 hour)

**Total Estimated Time: 1-2 days**

---

## 📝 Summary

| Aspect | Decision |
|--------|----------|
| **Primary Storage** | Cloudflare R2 ⭐ |
| **Reason** | 97% cost savings, S3-compatible, excellent performance |
| **Fallback** | Amazon S3 (easy migration if needed) |
| **Optional Feature** | Google Drive export (future enhancement) |
| **Implementation Time** | 1-2 days |
| **Cost (Year 1)** | ~$5/year vs $222/year with S3 |

---

**Status:** 🟡 **Awaiting Green Light to Implement**

**Questions?** Please comment on the GitHub issue with any questions or concerns.

---

**Created by:** GitHub Copilot Workspace  
**Last Updated:** October 29, 2025  
**Document Version:** 1.0
