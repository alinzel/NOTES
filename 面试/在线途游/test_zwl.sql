/*
Navicat MySQL Data Transfer

Source Server         : 10
Source Server Version : 50554
Source Host           : 192.168.200.10:3306
Source Database       : test_zwl

Target Server Type    : MYSQL
Target Server Version : 50554
File Encoding         : 65001

Date: 2019-04-16 20:05:31
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for `app_course`
-- ----------------------------
DROP TABLE IF EXISTS `app_course`;
CREATE TABLE `app_course` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `C_num` int(11) NOT NULL,
  `C_name` varchar(255) NOT NULL,
  `C_teacher_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `app_course_C_teacher_id_ea54448f_fk_app_teacher_id` (`C_teacher_id`),
  CONSTRAINT `app_course_C_teacher_id_ea54448f_fk_app_teacher_id` FOREIGN KEY (`C_teacher_id`) REFERENCES `app_teacher` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of app_course
-- ----------------------------
INSERT INTO `app_course` VALUES ('1', '1', '课程1', '1');
INSERT INTO `app_course` VALUES ('2', '2', '课程2', '3');
INSERT INTO `app_course` VALUES ('3', '3', '课程3', '3');
INSERT INTO `app_course` VALUES ('4', '4', '课程4', '2');

-- ----------------------------
-- Table structure for `app_score`
-- ----------------------------
DROP TABLE IF EXISTS `app_score`;
CREATE TABLE `app_score` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `S_score` int(11) NOT NULL,
  `S_course_id` int(11) NOT NULL,
  `S_student_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `app_score_S_course_id_fb520cf2_fk_app_course_id` (`S_course_id`),
  KEY `app_score_S_student_id_77a9d1d2_fk_app_student_id` (`S_student_id`),
  CONSTRAINT `app_score_S_student_id_77a9d1d2_fk_app_student_id` FOREIGN KEY (`S_student_id`) REFERENCES `app_student` (`id`),
  CONSTRAINT `app_score_S_course_id_fb520cf2_fk_app_course_id` FOREIGN KEY (`S_course_id`) REFERENCES `app_course` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of app_score
-- ----------------------------
INSERT INTO `app_score` VALUES ('1', '99', '1', '1');
INSERT INTO `app_score` VALUES ('2', '60', '2', '1');
INSERT INTO `app_score` VALUES ('3', '60', '1', '2');
INSERT INTO `app_score` VALUES ('4', '59', '4', '1');
INSERT INTO `app_score` VALUES ('5', '65', '4', '2');
INSERT INTO `app_score` VALUES ('6', '40', '4', '2');

-- ----------------------------
-- Table structure for `app_student`
-- ----------------------------
DROP TABLE IF EXISTS `app_student`;
CREATE TABLE `app_student` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `S_num` int(11) NOT NULL,
  `S_name` varchar(255) NOT NULL,
  `S_age` int(11) NOT NULL,
  `S_sex` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of app_student
-- ----------------------------
INSERT INTO `app_student` VALUES ('1', '1', '学生1', '18', '男');
INSERT INTO `app_student` VALUES ('2', '2', '学生2', '20', '女');
INSERT INTO `app_student` VALUES ('3', '3', '学生3', '22', '男');

-- ----------------------------
-- Table structure for `app_teacher`
-- ----------------------------
DROP TABLE IF EXISTS `app_teacher`;
CREATE TABLE `app_teacher` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `T_num` int(11) NOT NULL,
  `T_name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of app_teacher
-- ----------------------------
INSERT INTO `app_teacher` VALUES ('1', '1', '李银萍');
INSERT INTO `app_teacher` VALUES ('2', '2', '小李老师');
INSERT INTO `app_teacher` VALUES ('3', '3', '刘璐');

-- ----------------------------
-- Table structure for `auth_group`
-- ----------------------------
DROP TABLE IF EXISTS `auth_group`;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of auth_group
-- ----------------------------

-- ----------------------------
-- Table structure for `auth_group_permissions`
-- ----------------------------
DROP TABLE IF EXISTS `auth_group_permissions`;
CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of auth_group_permissions
-- ----------------------------

-- ----------------------------
-- Table structure for `auth_permission`
-- ----------------------------
DROP TABLE IF EXISTS `auth_permission`;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of auth_permission
-- ----------------------------
INSERT INTO `auth_permission` VALUES ('1', 'Can add log entry', '1', 'add_logentry');
INSERT INTO `auth_permission` VALUES ('2', 'Can change log entry', '1', 'change_logentry');
INSERT INTO `auth_permission` VALUES ('3', 'Can delete log entry', '1', 'delete_logentry');
INSERT INTO `auth_permission` VALUES ('4', 'Can add permission', '2', 'add_permission');
INSERT INTO `auth_permission` VALUES ('5', 'Can change permission', '2', 'change_permission');
INSERT INTO `auth_permission` VALUES ('6', 'Can delete permission', '2', 'delete_permission');
INSERT INTO `auth_permission` VALUES ('7', 'Can add group', '3', 'add_group');
INSERT INTO `auth_permission` VALUES ('8', 'Can change group', '3', 'change_group');
INSERT INTO `auth_permission` VALUES ('9', 'Can delete group', '3', 'delete_group');
INSERT INTO `auth_permission` VALUES ('10', 'Can add user', '4', 'add_user');
INSERT INTO `auth_permission` VALUES ('11', 'Can change user', '4', 'change_user');
INSERT INTO `auth_permission` VALUES ('12', 'Can delete user', '4', 'delete_user');
INSERT INTO `auth_permission` VALUES ('13', 'Can add content type', '5', 'add_contenttype');
INSERT INTO `auth_permission` VALUES ('14', 'Can change content type', '5', 'change_contenttype');
INSERT INTO `auth_permission` VALUES ('15', 'Can delete content type', '5', 'delete_contenttype');
INSERT INTO `auth_permission` VALUES ('16', 'Can add session', '6', 'add_session');
INSERT INTO `auth_permission` VALUES ('17', 'Can change session', '6', 'change_session');
INSERT INTO `auth_permission` VALUES ('18', 'Can delete session', '6', 'delete_session');
INSERT INTO `auth_permission` VALUES ('19', 'Can add course', '7', 'add_course');
INSERT INTO `auth_permission` VALUES ('20', 'Can change course', '7', 'change_course');
INSERT INTO `auth_permission` VALUES ('21', 'Can delete course', '7', 'delete_course');
INSERT INTO `auth_permission` VALUES ('22', 'Can add score', '8', 'add_score');
INSERT INTO `auth_permission` VALUES ('23', 'Can change score', '8', 'change_score');
INSERT INTO `auth_permission` VALUES ('24', 'Can delete score', '8', 'delete_score');
INSERT INTO `auth_permission` VALUES ('25', 'Can add student', '9', 'add_student');
INSERT INTO `auth_permission` VALUES ('26', 'Can change student', '9', 'change_student');
INSERT INTO `auth_permission` VALUES ('27', 'Can delete student', '9', 'delete_student');
INSERT INTO `auth_permission` VALUES ('28', 'Can add teacher', '10', 'add_teacher');
INSERT INTO `auth_permission` VALUES ('29', 'Can change teacher', '10', 'change_teacher');
INSERT INTO `auth_permission` VALUES ('30', 'Can delete teacher', '10', 'delete_teacher');

-- ----------------------------
-- Table structure for `auth_user`
-- ----------------------------
DROP TABLE IF EXISTS `auth_user`;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of auth_user
-- ----------------------------

-- ----------------------------
-- Table structure for `auth_user_groups`
-- ----------------------------
DROP TABLE IF EXISTS `auth_user_groups`;
CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of auth_user_groups
-- ----------------------------

-- ----------------------------
-- Table structure for `auth_user_user_permissions`
-- ----------------------------
DROP TABLE IF EXISTS `auth_user_user_permissions`;
CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of auth_user_user_permissions
-- ----------------------------

-- ----------------------------
-- Table structure for `django_admin_log`
-- ----------------------------
DROP TABLE IF EXISTS `django_admin_log`;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of django_admin_log
-- ----------------------------

-- ----------------------------
-- Table structure for `django_content_type`
-- ----------------------------
DROP TABLE IF EXISTS `django_content_type`;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of django_content_type
-- ----------------------------
INSERT INTO `django_content_type` VALUES ('1', 'admin', 'logentry');
INSERT INTO `django_content_type` VALUES ('7', 'app', 'course');
INSERT INTO `django_content_type` VALUES ('8', 'app', 'score');
INSERT INTO `django_content_type` VALUES ('9', 'app', 'student');
INSERT INTO `django_content_type` VALUES ('10', 'app', 'teacher');
INSERT INTO `django_content_type` VALUES ('3', 'auth', 'group');
INSERT INTO `django_content_type` VALUES ('2', 'auth', 'permission');
INSERT INTO `django_content_type` VALUES ('4', 'auth', 'user');
INSERT INTO `django_content_type` VALUES ('5', 'contenttypes', 'contenttype');
INSERT INTO `django_content_type` VALUES ('6', 'sessions', 'session');

-- ----------------------------
-- Table structure for `django_migrations`
-- ----------------------------
DROP TABLE IF EXISTS `django_migrations`;
CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of django_migrations
-- ----------------------------
INSERT INTO `django_migrations` VALUES ('1', 'contenttypes', '0001_initial', '2019-04-16 09:11:50');
INSERT INTO `django_migrations` VALUES ('2', 'auth', '0001_initial', '2019-04-16 09:11:52');
INSERT INTO `django_migrations` VALUES ('3', 'admin', '0001_initial', '2019-04-16 09:11:52');
INSERT INTO `django_migrations` VALUES ('4', 'admin', '0002_logentry_remove_auto_add', '2019-04-16 09:11:52');
INSERT INTO `django_migrations` VALUES ('5', 'app', '0001_initial', '2019-04-16 09:11:53');
INSERT INTO `django_migrations` VALUES ('6', 'contenttypes', '0002_remove_content_type_name', '2019-04-16 09:11:53');
INSERT INTO `django_migrations` VALUES ('7', 'auth', '0002_alter_permission_name_max_length', '2019-04-16 09:11:53');
INSERT INTO `django_migrations` VALUES ('8', 'auth', '0003_alter_user_email_max_length', '2019-04-16 09:11:53');
INSERT INTO `django_migrations` VALUES ('9', 'auth', '0004_alter_user_username_opts', '2019-04-16 09:11:53');
INSERT INTO `django_migrations` VALUES ('10', 'auth', '0005_alter_user_last_login_null', '2019-04-16 09:11:53');
INSERT INTO `django_migrations` VALUES ('11', 'auth', '0006_require_contenttypes_0002', '2019-04-16 09:11:53');
INSERT INTO `django_migrations` VALUES ('12', 'auth', '0007_alter_validators_add_error_messages', '2019-04-16 09:11:53');
INSERT INTO `django_migrations` VALUES ('13', 'auth', '0008_alter_user_username_max_length', '2019-04-16 09:11:53');
INSERT INTO `django_migrations` VALUES ('14', 'auth', '0009_alter_user_last_name_max_length', '2019-04-16 09:11:53');
INSERT INTO `django_migrations` VALUES ('15', 'sessions', '0001_initial', '2019-04-16 09:11:54');

-- ----------------------------
-- Table structure for `django_session`
-- ----------------------------
DROP TABLE IF EXISTS `django_session`;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of django_session
-- ----------------------------
