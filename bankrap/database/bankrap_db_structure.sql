-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: localhost    Database: bankrap2
-- ------------------------------------------------------
-- Server version	8.0.43

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `account_borrowerprofile`
--

DROP TABLE IF EXISTS `account_borrowerprofile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `account_borrowerprofile` (
  `user_ptr_id` int NOT NULL,
  `income` decimal(12,2) NOT NULL,
  `credit_score` int NOT NULL,
  `employment_status` varchar(50) NOT NULL,
  `profile_created_date` date NOT NULL,
  PRIMARY KEY (`user_ptr_id`),
  CONSTRAINT `account_borrowerprof_user_ptr_id_2f4fd00b_fk_account_u` FOREIGN KEY (`user_ptr_id`) REFERENCES `account_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `account_lenderprofile`
--

DROP TABLE IF EXISTS `account_lenderprofile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `account_lenderprofile` (
  `user_ptr_id` int NOT NULL,
  `investment_preference` varchar(200) NOT NULL,
  `available_funds` decimal(12,2) NOT NULL,
  `min_investment_amount` decimal(12,2) NOT NULL,
  `profile_created_date` date NOT NULL,
  PRIMARY KEY (`user_ptr_id`),
  CONSTRAINT `account_lenderprofil_user_ptr_id_5d0441ba_fk_account_u` FOREIGN KEY (`user_ptr_id`) REFERENCES `account_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `account_user`
--

DROP TABLE IF EXISTS `account_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `account_user` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `student_id` varchar(20) DEFAULT NULL,
  `name` varchar(40) NOT NULL,
  `email` varchar(254) NOT NULL,
  `password` varchar(40) NOT NULL,
  `address` varchar(40) NOT NULL,
  `contact_number` varchar(20) NOT NULL,
  `type` varchar(1) NOT NULL,
  `school_id_file` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `student_id` (`student_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=65 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `loan_activeloan`
--

DROP TABLE IF EXISTS `loan_activeloan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `loan_activeloan` (
  `active_loan_id` int NOT NULL AUTO_INCREMENT,
  `principal_amount` decimal(12,2) NOT NULL,
  `interest_rate` decimal(5,2) NOT NULL,
  `total_repayment` decimal(12,2) NOT NULL,
  `start_date` date NOT NULL,
  `due_date` date NOT NULL,
  `status` varchar(20) NOT NULL,
  `borrower_id` int NOT NULL,
  `lender_id` int NOT NULL,
  `loan_request_id` int NOT NULL,
  PRIMARY KEY (`active_loan_id`),
  UNIQUE KEY `loan_request_id` (`loan_request_id`),
  KEY `loan_activeloan_borrower_id_4606be99_fk_account_user_user_id` (`borrower_id`),
  KEY `loan_activeloan_lender_id_f4b315d6_fk_account_user_user_id` (`lender_id`),
  CONSTRAINT `loan_activeloan_borrower_id_4606be99_fk_account_user_user_id` FOREIGN KEY (`borrower_id`) REFERENCES `account_user` (`user_id`),
  CONSTRAINT `loan_activeloan_lender_id_f4b315d6_fk_account_user_user_id` FOREIGN KEY (`lender_id`) REFERENCES `account_user` (`user_id`),
  CONSTRAINT `loan_activeloan_loan_request_id_7a0e6cf9_fk_loan_loan` FOREIGN KEY (`loan_request_id`) REFERENCES `loan_loanrequest` (`loan_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `loan_loanoffer`
--

DROP TABLE IF EXISTS `loan_loanoffer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `loan_loanoffer` (
  `offer_id` int NOT NULL AUTO_INCREMENT,
  `offered_amount` decimal(12,2) NOT NULL,
  `offered_rate` decimal(5,2) NOT NULL,
  `message` longtext,
  `status` varchar(20) NOT NULL,
  `offer_date` datetime(6) NOT NULL,
  `lender_id` int NOT NULL,
  `loan_request_id` int NOT NULL,
  PRIMARY KEY (`offer_id`),
  KEY `loan_loanoffer_lender_id_826317ff_fk_account_user_user_id` (`lender_id`),
  KEY `loan_loanoffer_loan_request_id_461421a2_fk_loan_loan` (`loan_request_id`),
  CONSTRAINT `loan_loanoffer_lender_id_826317ff_fk_account_user_user_id` FOREIGN KEY (`lender_id`) REFERENCES `account_user` (`user_id`),
  CONSTRAINT `loan_loanoffer_loan_request_id_461421a2_fk_loan_loan` FOREIGN KEY (`loan_request_id`) REFERENCES `loan_loanrequest` (`loan_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `loan_loanrequest`
--

DROP TABLE IF EXISTS `loan_loanrequest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `loan_loanrequest` (
  `loan_id` int NOT NULL AUTO_INCREMENT,
  `amount` decimal(12,2) NOT NULL,
  `interest_rate` decimal(5,2) NOT NULL,
  `term` varchar(20) NOT NULL,
  `purpose` longtext NOT NULL,
  `status` varchar(20) NOT NULL,
  `request_date` datetime(6) NOT NULL,
  `borrower_id` int NOT NULL,
  PRIMARY KEY (`loan_id`),
  KEY `loan_loanrequest_borrower_id_2a0af2f8_fk_account_user_user_id` (`borrower_id`),
  CONSTRAINT `loan_loanrequest_borrower_id_2a0af2f8_fk_account_user_user_id` FOREIGN KEY (`borrower_id`) REFERENCES `account_user` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `review_reviewandrating`
--

DROP TABLE IF EXISTS `review_reviewandrating`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `review_reviewandrating` (
  `review_id` int NOT NULL AUTO_INCREMENT,
  `rating` smallint unsigned NOT NULL,
  `comment` longtext NOT NULL,
  `review_date` datetime(6) NOT NULL,
  `review_type` varchar(3) NOT NULL,
  `loan_id` int NOT NULL,
  `reviewee_id` int NOT NULL,
  `reviewer_id` int NOT NULL,
  PRIMARY KEY (`review_id`),
  UNIQUE KEY `review_reviewandrating_loan_id_reviewer_id_13b5b1f4_uniq` (`loan_id`,`reviewer_id`),
  KEY `review_reviewandrati_reviewee_id_34a7a68b_fk_account_u` (`reviewee_id`),
  KEY `review_reviewandrati_reviewer_id_4dfeb476_fk_account_u` (`reviewer_id`),
  CONSTRAINT `review_reviewandrati_loan_id_7d73111b_fk_loan_loan` FOREIGN KEY (`loan_id`) REFERENCES `loan_loanrequest` (`loan_id`),
  CONSTRAINT `review_reviewandrati_reviewee_id_34a7a68b_fk_account_u` FOREIGN KEY (`reviewee_id`) REFERENCES `account_user` (`user_id`),
  CONSTRAINT `review_reviewandrati_reviewer_id_4dfeb476_fk_account_u` FOREIGN KEY (`reviewer_id`) REFERENCES `account_user` (`user_id`),
  CONSTRAINT `review_reviewandrating_chk_1` CHECK ((`rating` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `transaction_transaction`
--

DROP TABLE IF EXISTS `transaction_transaction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transaction_transaction` (
  `transaction_id` int NOT NULL AUTO_INCREMENT,
  `amount` decimal(12,2) NOT NULL,
  `transaction_data` varchar(255) NOT NULL,
  `type` varchar(1) NOT NULL,
  `status` varchar(1) NOT NULL,
  `reference_number` varchar(50) DEFAULT NULL,
  `transaction_date` datetime(6) NOT NULL,
  `loan_request_id` int DEFAULT NULL,
  `user_id` int DEFAULT NULL,
  PRIMARY KEY (`transaction_id`),
  KEY `transaction_transact_loan_request_id_df3b6820_fk_loan_loan` (`loan_request_id`),
  KEY `transaction_transaction_user_id_9105ab00_fk_account_user_user_id` (`user_id`),
  CONSTRAINT `transaction_transact_loan_request_id_df3b6820_fk_loan_loan` FOREIGN KEY (`loan_request_id`) REFERENCES `loan_loanrequest` (`loan_id`),
  CONSTRAINT `transaction_transaction_user_id_9105ab00_fk_account_user_user_id` FOREIGN KEY (`user_id`) REFERENCES `account_user` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wallet_wallet`
--

DROP TABLE IF EXISTS `wallet_wallet`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wallet_wallet` (
  `wallet_id` int NOT NULL AUTO_INCREMENT,
  `balance` decimal(12,2) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`wallet_id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `wallet_wallet_user_id_8c75caaa_fk_account_user_user_id` FOREIGN KEY (`user_id`) REFERENCES `account_user` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wallet_wallettransaction`
--

DROP TABLE IF EXISTS `wallet_wallettransaction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wallet_wallettransaction` (
  `transaction_id` int NOT NULL AUTO_INCREMENT,
  `amount` decimal(12,2) NOT NULL,
  `transaction_type` varchar(10) NOT NULL,
  `reference_number` varchar(50) DEFAULT NULL,
  `transaction_date` datetime(6) NOT NULL,
  `wallet_id` int NOT NULL,
  PRIMARY KEY (`transaction_id`),
  KEY `wallet_wallettransac_wallet_id_b438357c_fk_wallet_wa` (`wallet_id`),
  CONSTRAINT `wallet_wallettransac_wallet_id_b438357c_fk_wallet_wa` FOREIGN KEY (`wallet_id`) REFERENCES `wallet_wallet` (`wallet_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping routines for database 'bankrap2'
--
/*!50003 DROP PROCEDURE IF EXISTS `authenticate_user` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `authenticate_user`(
    IN p_identity VARCHAR(255),
    IN p_password VARCHAR(40),
    OUT p_out_user_id INT 
)
BEGIN
    DECLARE v_user_id INT DEFAULT NULL;

    SELECT user_id 
    INTO v_user_id
    FROM account_user
    WHERE (email = p_identity OR student_id = p_identity)
      AND password = p_password
    LIMIT 1;

    IF v_user_id IS NOT NULL THEN
        SET p_out_user_id = v_user_id;
    ELSE
        SET p_out_user_id = NULL; 
    END IF;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `CreateOrUpdateReview` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `CreateOrUpdateReview`(
    IN p_loan_id INT,
    IN p_reviewer_id INT,
    IN p_reviewee_id INT,
    IN p_rating INT,
    IN p_comment TEXT,
    IN p_review_type VARCHAR(3)
)
BEGIN
    DECLARE v_existing_review_id INT DEFAULT NULL;
    DECLARE v_action VARCHAR(10);
    
    -- Check if review already exists
    SELECT review_id INTO v_existing_review_id
    FROM review_reviewandrating
    WHERE loan_id = p_loan_id AND reviewer_id = p_reviewer_id
    LIMIT 1;
    
    IF v_existing_review_id IS NOT NULL THEN
        -- Update existing review
        UPDATE review_reviewandrating
        SET 
            rating = p_rating,
            comment = p_comment,
            review_date = NOW()
        WHERE review_id = v_existing_review_id;
        
        SET v_action = 'updated';
    ELSE
        -- Create new review
        INSERT INTO review_reviewandrating (
            loan_id, reviewer_id, reviewee_id, 
            rating, comment, review_date, review_type
        ) VALUES (
            p_loan_id, p_reviewer_id, p_reviewee_id,
            p_rating, p_comment, NOW(), p_review_type
        );
        
        SET v_action = 'created';
        SET v_existing_review_id = LAST_INSERT_ID();
    END IF;
    
    -- Return the review data
    SELECT 
        r.review_id,
        r.rating,
        r.comment,
        r.review_date,
        r.review_type,
        reviewee.name as reviewee_name,
        reviewer.name as reviewer_name,
        lr.amount as loan_amount,
        lr.purpose as loan_purpose,
        v_action as action_taken
    FROM review_reviewandrating r
    JOIN account_user reviewee ON r.reviewee_id = reviewee.user_id
    JOIN account_user reviewer ON r.reviewer_id = reviewer.user_id
    JOIN loan_loanrequest lr ON r.loan_id = lr.loan_id
    WHERE r.review_id = v_existing_review_id;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `create_user_and_wallet` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `create_user_and_wallet`(
    IN p_name VARCHAR(40),
    IN p_student_id VARCHAR(20),
    IN p_email VARCHAR(254),
    IN p_password VARCHAR(40),
    IN p_address VARCHAR(40),
    IN p_contact_number VARCHAR(20),
    IN p_type CHAR(1),
    IN p_school_id_file_path VARCHAR(100),
    OUT p_out_user_id INT
)
    MODIFIES SQL DATA
BEGIN
    DECLARE v_new_user_id INT;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_out_user_id = NULL;
        RESIGNAL;
    END;

    START TRANSACTION;

    INSERT INTO account_user (student_id, name, email, password, address, contact_number, type, school_id_file)
    VALUES (p_student_id, p_name, p_email, p_password, p_address, p_contact_number, p_type, p_school_id_file_path);

    SET v_new_user_id = LAST_INSERT_ID();

    IF p_type = 'L' THEN
        INSERT INTO account_lenderprofile (user_ptr_id, investment_preference, available_funds, min_investment_amount, profile_created_date)
        VALUES (v_new_user_id, '', 0.00, 500.00, CURDATE());
    ELSE
        INSERT INTO account_borrowerprofile (user_ptr_id, income, credit_score, employment_status, profile_created_date)
        VALUES (v_new_user_id, 0.00, 0, '', CURDATE());
    END IF;

    INSERT INTO wallet_wallet (user_id, balance, created_at)
    VALUES (v_new_user_id, 0.00, NOW());

    COMMIT;

    SET p_out_user_id = v_new_user_id;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `GetUserReviews` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `GetUserReviews`(
    IN p_user_id INT,
    IN p_review_type VARCHAR(10)
)
BEGIN
    IF p_review_type = 'received' THEN
        -- Get reviews received by the user
        SELECT 
            r.review_id,
            r.rating,
            r.comment,
            r.review_date,
            r.review_type,
            r.loan_id,
            r.reviewer_id,
            r.reviewee_id,
            reviewer.name as other_user_name,
            reviewer.type as other_user_type,
            lr.amount as loan_amount,
            lr.purpose as loan_purpose
        FROM review_reviewandrating r
        JOIN account_user reviewer ON r.reviewer_id = reviewer.user_id
        JOIN loan_loanrequest lr ON r.loan_id = lr.loan_id
        WHERE r.reviewee_id = p_user_id
        ORDER BY r.review_date DESC;
    ELSE
        -- Get reviews given by the user
        SELECT 
            r.review_id,
            r.rating,
            r.comment,
            r.review_date,
            r.review_type,
            r.loan_id,
            r.reviewer_id,
            r.reviewee_id,
            reviewee.name as other_user_name,
            reviewee.type as other_user_type,
            lr.amount as loan_amount,
            lr.purpose as loan_purpose
        FROM review_reviewandrating r
        JOIN account_user reviewee ON r.reviewee_id = reviewee.user_id
        JOIN loan_loanrequest lr ON r.loan_id = lr.loan_id
        WHERE r.reviewer_id = p_user_id
        ORDER BY r.review_date DESC;
    END IF;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `GetUserReviewStats` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `GetUserReviewStats`(
    IN p_user_id INT
)
BEGIN
    SELECT 
        COALESCE(AVG(rating), 0) as avg_rating,
        COUNT(*) as total_reviews,
        COALESCE(SUM(CASE WHEN rating = 5 THEN 1 ELSE 0 END), 0) as five_star,
        COALESCE(SUM(CASE WHEN rating = 4 THEN 1 ELSE 0 END), 0) as four_star,
        COALESCE(SUM(CASE WHEN rating = 3 THEN 1 ELSE 0 END), 0) as three_star,
        COALESCE(SUM(CASE WHEN rating = 2 THEN 1 ELSE 0 END), 0) as two_star,
        COALESCE(SUM(CASE WHEN rating = 1 THEN 1 ELSE 0 END), 0) as one_star
    FROM review_reviewandrating
    WHERE reviewee_id = p_user_id;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_user_profile` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `get_user_profile`(
    IN p_user_id INT
)
    READS SQL DATA
BEGIN
    DECLARE v_user_type CHAR(1);

    SELECT type INTO v_user_type
    FROM account_user
    WHERE user_id = p_user_id
    LIMIT 1;

    IF v_user_type = 'B' THEN
        SELECT AU.*, BP.income, BP.credit_score, BP.employment_status
        FROM account_user AU
        JOIN account_borrowerprofile BP ON AU.user_id = BP.user_ptr_id
        WHERE AU.user_id = p_user_id;
    ELSEIF v_user_type = 'L' THEN
        SELECT AU.*, LP.investment_preference, LP.available_funds, LP.min_investment_amount
        FROM account_user AU
        JOIN account_lenderprofile LP ON AU.user_id = LP.user_ptr_id
        WHERE AU.user_id = p_user_id;
    ELSE
        SELECT * FROM account_user WHERE user_id = p_user_id;
    END IF;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `update_user_profile` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `update_user_profile`(
    IN p_user_id INT,
    IN p_name VARCHAR(40),
    IN p_address VARCHAR(40),
    IN p_contact_number VARCHAR(20),
    IN p_email VARCHAR(254),
    -- Borrower-specific fields
    IN p_income DECIMAL(12, 2),
    IN p_employment_status VARCHAR(50),
    -- Lender-specific fields
    IN p_min_investment_amount DECIMAL(12, 2),
    IN p_investment_preference VARCHAR(200)
)
BEGIN
    DECLARE v_user_type CHAR(1);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    SELECT type INTO v_user_type
    FROM account_user
    WHERE user_id = p_user_id;

    UPDATE account_user
    SET
        name = p_name,
        address = p_address,
        contact_number = p_contact_number,
        email = p_email
    WHERE user_id = p_user_id;

    IF v_user_type = 'B' THEN
        UPDATE account_borrowerprofile
        SET
            income = p_income,
            employment_status = p_employment_status
        WHERE user_ptr_id = p_user_id;
    ELSEIF v_user_type = 'L' THEN
        UPDATE account_lenderprofile
        SET
            min_investment_amount = p_min_investment_amount,
            investment_preference = p_investment_preference
        WHERE user_ptr_id = p_user_id;
    END IF;

    COMMIT;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-17 21:33:22
