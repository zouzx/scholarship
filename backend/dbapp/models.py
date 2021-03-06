from django.db import models
## general dicts
GENDER_TO_NAME = {'male':'男', 'female': '女'}
DEPARTMENT_TO_NAME = {
        "media": "媒体所",
        "cad": "CAD所",
        "hi_perf": "高性能所",
        "ai": "人智所",
        "software": "软件所",
        "network": "网络所",
        "gix": "GIX所",
        "cs_ma": "计研"
}

# Create your models here.
class User(models.Model):
    GENDER_CHOICES = (
        ('male', 'male'),
        ('female', 'female'),
    )
    DEPARTMENT_CHOICES = (
        ('media', 'media'),
        ('cad', 'cad'),
        ('hi_perf', 'hi_perf'),
        ('ai', 'ai'),
        ('software', 'software'),
        ('network', 'network'),
        ('gix', 'gix'),
        ('cs_ma', 'cs_ma')
    )
    SPECIFIC_STUDENT_TYPE = (
        ('master', 'master'),
        ('doctor_straight', 'doctor_straight'),
        ('master_doctor', 'master_doctor'),
        ('doctor_normal', 'doctor_normal')
    )
    GRADE_CHOICES = (
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('above', 'above')
    )
    STUDENT_STATUS_CHOICES = (
        ('cst', 'cst'),
        ('shenzhen', 'shenzhen'),
        ('other', 'other')
    )
    POLITICAL_STATUS_CHOICES = (
        ('party', 'party'),
        ('pre_party', 'pre_party'),
        ('league', 'league'),
        ('general', 'general'),
        ('other', 'other')
    )
    ## basic user info
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(db_index=True, max_length=100, unique=True)
    password = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    student_id = models.CharField(db_index=True, max_length=30)
    user_type = models.IntegerField(null=False, default=0)
    ## user_type: 0 for student, 1 for teacher, 2 for admin
    ## extended user info
    class_name = models.CharField(max_length=30)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    department = models.CharField(max_length=15, choices=DEPARTMENT_CHOICES)
    student_type = models.CharField(max_length=25, choices=SPECIFIC_STUDENT_TYPE)
    grade = models.CharField(max_length=10, choices=GRADE_CHOICES)
    student_status = models.CharField(max_length=10, choices=STUDENT_STATUS_CHOICES)
    political_status = models.CharField(max_length=15, choices=POLITICAL_STATUS_CHOICES)
    ethnic_group = models.CharField(max_length=100)
    instructor = models.CharField(max_length=30)
    email = models.EmailField()
    mobile = models.CharField(max_length=30)
    address = models.CharField(max_length=200)
    post_code = models.CharField(max_length=20)
    is_project_started = models.BooleanField(default=False)
    ## self-maintained info
    register_date = models.DateTimeField(auto_now_add=True)
    last_modify = models.DateTimeField(auto_now=True)    

class Log(models.Model):
    id = models.AutoField(primary_key=True)
    action = models.CharField(max_length=100)
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    details = models.TextField(max_length=1000)
    ip = models.CharField(max_length=100)
    time = models.DateTimeField(auto_now_add=True)

class Notify(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    date = models.DateTimeField(db_index=True, auto_now_add=True)
    link = models.TextField()

"""
Dependency chain:

Apply Material <- Score Rule <- Apply Info
"""
class ApplyMaterialSetting(models.Model):
    apply_material_id = models.AutoField(primary_key=True)
    alias = models.CharField(db_index=True, max_length=200, unique=True)       ### alias for a rule, e.g. 计算机系奖学金申请材料模板
    json = models.TextField()  ### json settings for frontend, @see template data in corresponding js file
    set_time = models.DateTimeField(auto_now_add=True)

class ApplyScoreRuleSetting(models.Model):
    apply_score_rule_id = models.AutoField(primary_key=True)
    alias = models.CharField(db_index=True, max_length=200, unique=True)
    json = models.TextField()
    set_time = models.DateTimeField(auto_now_add=True)
    apply_material_id = models.ForeignKey(ApplyMaterialSetting, on_delete=models.CASCADE)  ## Rules are only compatible with corresponding material setting

"""
Defines the apply info, e.g. Scholarship name, score_rule
"""
class ApplyInfoSetting(models.Model):
    apply_info_id = models.AutoField(primary_key=True)
    scholarship_name = models.CharField(db_index=True, max_length=200, unique=True)
    apply_score_rule_id = models.ForeignKey(ApplyScoreRuleSetting, on_delete=models.CASCADE)
    set_time = models.DateTimeField(auto_now_add=True)
    can_apply = models.BooleanField(default=False)

"""
Apply info for a user (Unique for the same scholarship)
Note that if admin changes material settings(in other words, generates a new material id), previous records should be invalidated;
if admin changes score rule settings, the score of the students will be re-evaluated

We use lazy method to calculate the score, that is, we only calculate it iff. `is_score_updated` is False
If `json` or `apply_score_rule_id` is changed, we should set is_score_updated to False

Way to extract data (of a certain scholarship):
find apply_info_id == current_apply_info_id && is_user_confirm, update score if necessary, output value
"""
class ApplyInfo(models.Model):
    class Meta:
        ## a user can have only one application for a single scholarship
        unique_together = ("user_id", "apply_info_id")
    apply_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    json = models.TextField()
    apply_info_id = models.ForeignKey(ApplyInfoSetting, on_delete=models.CASCADE)
    apply_date = models.DateTimeField(db_index=True, auto_now_add=True)
    score = models.FloatField(db_index=True, null=False, default=0)
    extra_score = models.FloatField(null=False, default=0)
    academic_score = models.FloatField(null=False, default=0)
    work_score = models.FloatField(null=False, default=0)
    teacher_score = models.FloatField(null=False, default=0)
    teacher_score_avg = models.FloatField(null=False, default=0)
    wrong_time = models.BooleanField(default=False)
    extra_info = models.TextField()
    is_score_updated = models.BooleanField(default=False)
    is_teacher_score_updated = models.BooleanField(default=False)
    is_user_confirm = models.BooleanField(default=False)  ### If user saves temporarily, this field will be False
    report_num = models.IntegerField(default=0)

class TeacherScore(models.Model):
    class Meta:
        # a teacher cannot score a single entry twice
        unique_together = ("apply_id", "teacher_id")
    apply_id = models.ForeignKey(ApplyInfo, on_delete=models.CASCADE)
    teacher_id = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.FloatField(null=False, default=0)

class SessionToken(models.Model):
    user = models.OneToOneField(User, models.CASCADE)
    token = models.CharField(max_length=64, db_index=True)
    set_time = models.DateTimeField(auto_now_add=True)

def LogAction(action, username, ip, details=''):
    Log.objects.create(action=action,username=username, details=details,ip=ip)
