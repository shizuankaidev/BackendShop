from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

from company.models import Company


# =========================================================
# VALIDADORES
# =========================================================

def validate_product_image(image):

    allowed_types = [
        "image/png",
        "image/jpeg",
        "image/webp",
    ]

    if image.content_type not in allowed_types:
        raise ValidationError(
            "Formato inválido."
        )

    max_size = 5 * 1024 * 1024

    if image.size > max_size:
        raise ValidationError(
            "Imagem muito grande. Máximo 5MB."
        )


# =========================================================
# BASE MODEL
# =========================================================

class BaseModel(models.Model):

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    is_active = models.BooleanField(
        default=True
    )

    class Meta:
        abstract = True


# =========================================================
# CATEGORY
# =========================================================

class Category(BaseModel):

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="categories"
    )

    name = models.CharField(
        max_length=120
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    class Meta:
        unique_together = (
            "company",
            "name"
        )

        ordering = ["name"]

    def __str__(self):
        return self.name


# =========================================================
# PRODUCT
# =========================================================

class Product(BaseModel):

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Ativo"
        INACTIVE = "INACTIVE", "Inativo"

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="products"
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name="products",
        null=True,
        blank=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_products",
        null=True
    )

    # =====================================================
    # IDENTIFICAÇÃO
    # =====================================================

    name = models.CharField(
        max_length=255
    )

    slug = models.SlugField(
        max_length=255,
        blank=True,
        null=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    short_description = models.CharField(
        max_length=300,
        blank=True,
        null=True
    )

    sku = models.CharField(
        max_length=120,
        blank=True,
        null=True
    )

    barcode = models.CharField(
        max_length=120,
        blank=True,
        null=True
    )

    # =====================================================
    # PREÇOS
    # =====================================================

    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    # =====================================================
    # ESTOQUE
    # =====================================================

    stock = models.IntegerField(
        default=0
    )

    min_stock = models.IntegerField(
        default=0
    )

    track_stock = models.BooleanField(
        default=True
    )

    # =====================================================
    # ATRIBUTOS
    # =====================================================

    weight = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        blank=True,
        null=True
    )

    width = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    height = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    length = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    # =====================================================
    # CONTROLE
    # =====================================================

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )

    featured = models.BooleanField(
        default=False
    )

    class Meta:

        ordering = ["-id"]

        indexes = [
            models.Index(fields=["company"]),
            models.Index(fields=["name"]),
            models.Index(fields=["sku"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return self.name

    # =====================================================
    # MÉTRICAS
    # =====================================================

    @property
    def profit(self):
        return self.sale_price - self.cost_price

    @property
    def margin(self):

        if self.cost_price <= 0:
            return 0

        return (
            (self.sale_price - self.cost_price)
            / self.cost_price
        ) * 100


# =========================================================
# PRODUCT IMAGE
# =========================================================

class ProductImage(BaseModel):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.ImageField(
        upload_to="products/",
        validators=[validate_product_image]
    )

    alt_text = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    is_primary = models.BooleanField(
        default=False
    )

    order = models.PositiveIntegerField(
        default=0
    )

    class Meta:
        ordering = ["order", "id"]

    def save(self, *args, **kwargs):

        if self.is_primary:

            ProductImage.objects.filter(
                product=self.product,
                is_primary=True
            ).update(is_primary=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Imagem - {self.product.name}"