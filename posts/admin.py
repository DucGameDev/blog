from django import forms
from django.contrib import admin
from django.utils import timezone
from import_export import resources, fields, widgets
from import_export.admin import ImportExportModelAdmin, ExportActionMixin
from .models import Post, Category, Subscriber, Comment


# ── Datetime widget ───────────────────────────────────────────────────────────

class DateTimeLocalInput(forms.DateTimeInput):
    input_type = 'datetime-local'

    def format_value(self, value):
        if value and hasattr(value, 'astimezone') and timezone.is_aware(value):
            value = timezone.localtime(value)
        return super().format_value(value)


class PostAdminForm(forms.ModelForm):
    published_at = forms.DateTimeField(
        widget=DateTimeLocalInput(format='%Y-%m-%dT%H:%M'),
        input_formats=['%Y-%m-%dT%H:%M'],
        required=False,
        label='Published at',
    )

    class Meta:
        model = Post
        fields = '__all__'


# ── Import/Export resource ────────────────────────────────────────────────────

class PostResource(resources.ModelResource):
    category = fields.Field(
        column_name='category',
        attribute='category',
        widget=widgets.ForeignKeyWidget(Category, field='name'),
    )
    author = fields.Field(
        column_name='author',
        attribute='author',
        widget=widgets.ForeignKeyWidget(
            __import__('django.contrib.auth', fromlist=['models']).models.User,
            field='username',
        ),
    )
    tags = fields.Field(column_name='tags', attribute=None)

    class Meta:
        model = Post
        import_id_fields = ('slug',)
        exclude = ('id', 'thumbnail', 'created_at', 'updated_at')
        export_order = (
            'slug', 'title', 'status', 'published_at',
            'excerpt', 'content',
            'author', 'category', 'tags',
            'reading_time', 'views',
            'meta_title', 'meta_description', 'note',
        )

    def dehydrate_tags(self, post):
        return ','.join(t.name for t in post.tags.all())

    def after_save_instance(self, instance, row, **kwargs):
        tag_str = row.get('tags', '')
        if tag_str:
            instance.tags.set(*[t.strip() for t in tag_str.split(',') if t.strip()])

    def before_import_row(self, row, row_number=None, **kwargs):
        # Ensure published_at is timezone-aware on import
        val = row.get('published_at')
        if val and isinstance(val, str) and val and '+' not in val and 'Z' not in val:
            row['published_at'] = val + '+07:00'


# ── Admin classes ─────────────────────────────────────────────────────────────

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Post)
class PostAdmin(ExportActionMixin, ImportExportModelAdmin):
    form = PostAdminForm
    resource_classes = [PostResource]
    list_display = ('thumbnail_preview', 'title', 'author', 'category', 'status', 'published_at', 'reading_time')

    @admin.display(description='Ảnh')
    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            from django.utils.html import format_html
            return format_html(
                '<img src="{}" style="width:72px;height:45px;object-fit:cover;border-radius:3px;">',
                obj.thumbnail.url
            )
        return '—'

    @admin.display(description='Xem trước ảnh bìa')
    def thumbnail_preview_large(self, obj):
        if obj.thumbnail:
            from django.utils.html import format_html
            return format_html(
                '<img src="{}" style="max-width:400px;width:100%;aspect-ratio:16/10;object-fit:cover;border-radius:4px;">',
                obj.thumbnail.url
            )
        return '(chưa có ảnh)'
    list_filter = ('status', 'category', 'author')
    search_fields = ('title', 'excerpt', 'content')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    ordering = ('-published_at',)
    readonly_fields = ('thumbnail_preview_large',)
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'author', 'category', 'tags')}),
        ('Content', {'fields': ('excerpt', 'content', 'thumbnail_preview_large', 'thumbnail')}),
        ('Publishing', {'fields': ('status', 'published_at')}),
        ('SEO', {'fields': ('meta_title', 'meta_description'), 'classes': ('collapse',)}),
        ('Ghi chú nội bộ', {'fields': ('note',), 'classes': ('collapse',)}),
    )


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at', 'active')
    list_filter = ('active',)
    search_fields = ('email',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'post', 'created_at', 'approved')
    list_filter = ('approved', 'created_at')
    search_fields = ('name', 'email', 'content')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(approved=True)
    approve_comments.short_description = 'Duyệt bình luận đã chọn'
