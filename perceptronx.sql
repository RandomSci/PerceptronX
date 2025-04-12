-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Apr 12, 2025 at 07:20 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `perceptronx`
--

-- --------------------------------------------------------

--
-- Table structure for table `Appointments`
--

CREATE TABLE `Appointments` (
  `appointment_id` int(11) NOT NULL,
  `patient_id` int(11) NOT NULL,
  `therapist_id` int(11) NOT NULL,
  `appointment_date` date NOT NULL,
  `appointment_time` time NOT NULL,
  `duration` int(11) DEFAULT 60,
  `status` enum('Scheduled','Completed','Cancelled','No-Show') DEFAULT 'Scheduled',
  `notes` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `ExerciseCategories`
--

CREATE TABLE `ExerciseCategories` (
  `category_id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `description` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `ExerciseCategories`
--

INSERT INTO `ExerciseCategories` (`category_id`, `name`, `description`) VALUES
(1, 'Lower Extremity', 'Exercises focusing on hip, knee, ankle and foot rehabilitation'),
(2, 'Upper Extremity', 'Exercises for shoulder, elbow, wrist and hand rehabilitation'),
(3, 'Spine', 'Exercises for cervical, thoracic and lumbar spine rehabilitation'),
(4, 'Balance', 'Exercises to improve stability and reduce fall risk'),
(5, 'Core Strengthening', 'Exercises targeting abdominal and back muscles'),
(6, 'Functional Training', 'Activities that mimic daily living and work tasks'),
(7, 'Post-Surgical', 'Rehabilitation protocols following surgical procedures'),
(8, 'Sports Rehabilitation', 'Specialized exercises for athletic recovery');

-- --------------------------------------------------------

--
-- Table structure for table `Exercises`
--

CREATE TABLE `Exercises` (
  `exercise_id` int(11) NOT NULL,
  `therapist_id` int(11) NOT NULL,
  `category_id` int(11) DEFAULT NULL,
  `name` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `video_url` varchar(255) DEFAULT NULL,
  `duration` int(11) DEFAULT NULL,
  `difficulty` enum('Beginner','Intermediate','Advanced') DEFAULT NULL,
  `instructions` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `feedback`
--

CREATE TABLE `feedback` (
  `feedback_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `message` text NOT NULL,
  `rating` int(11) DEFAULT NULL CHECK (`rating` between 1 and 5),
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `Messages`
--

CREATE TABLE `Messages` (
  `message_id` int(11) NOT NULL,
  `sender_id` int(11) NOT NULL,
  `sender_type` enum('therapist','patient','user') NOT NULL DEFAULT 'therapist',
  `recipient_id` int(11) NOT NULL,
  `recipient_type` enum('therapist','patient','user') NOT NULL DEFAULT 'therapist',
  `subject` varchar(100) DEFAULT NULL,
  `content` text NOT NULL,
  `is_read` tinyint(1) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `Messages`
--

INSERT INTO `Messages` (`message_id`, `sender_id`, `sender_type`, `recipient_id`, `recipient_type`, `subject`, `content`, `is_read`, `created_at`) VALUES
(11, 11, 'therapist', 10, 'therapist', 'Greetings', 'Hello!\r\n', 1, '2025-04-10 13:23:54'),
(13, 10, 'therapist', 11, 'therapist', 'Re: Greetings', 'Hello din po!', 1, '2025-04-10 13:24:32'),
(14, 11, 'therapist', 10, 'therapist', 'Re: Greetings', 'Kamusta?', 0, '2025-04-11 02:42:07'),
(15, 11, 'therapist', 10, 'therapist', 'Testing phase', 'Focus to succeed, not suck sid', 0, '2025-04-11 02:43:55');

-- --------------------------------------------------------

--
-- Table structure for table `PatientExerciseProgress`
--

CREATE TABLE `PatientExerciseProgress` (
  `progress_id` int(11) NOT NULL,
  `patient_id` int(11) NOT NULL,
  `plan_exercise_id` int(11) NOT NULL,
  `completion_date` date NOT NULL,
  `sets_completed` int(11) DEFAULT NULL,
  `repetitions_completed` int(11) DEFAULT NULL,
  `duration_seconds` int(11) DEFAULT NULL,
  `pain_level` int(11) DEFAULT NULL,
  `difficulty_level` int(11) DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `PatientMetrics`
--

CREATE TABLE `PatientMetrics` (
  `metric_id` int(11) NOT NULL,
  `patient_id` int(11) NOT NULL,
  `therapist_id` int(11) NOT NULL,
  `measurement_date` date NOT NULL,
  `adherence_rate` decimal(5,2) DEFAULT NULL,
  `pain_level` int(11) DEFAULT NULL,
  `functionality_score` int(11) DEFAULT NULL,
  `recovery_progress` decimal(5,2) DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `PatientNotes`
--

CREATE TABLE `PatientNotes` (
  `note_id` int(11) NOT NULL,
  `patient_id` int(11) NOT NULL,
  `therapist_id` int(11) NOT NULL,
  `appointment_id` int(11) DEFAULT NULL,
  `note_text` text NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `Patients`
--

CREATE TABLE `Patients` (
  `patient_id` int(11) NOT NULL,
  `therapist_id` int(11) NOT NULL,
  `first_name` varchar(255) NOT NULL,
  `last_name` varchar(255) NOT NULL,
  `email` varchar(255) DEFAULT NULL,
  `phone` varchar(50) DEFAULT NULL,
  `date_of_birth` date DEFAULT NULL,
  `address` text DEFAULT NULL,
  `diagnosis` varchar(255) DEFAULT NULL,
  `status` enum('Active','Inactive','At Risk') DEFAULT 'Active',
  `notes` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `Patients`
--

INSERT INTO `Patients` (`patient_id`, `therapist_id`, `first_name`, `last_name`, `email`, `phone`, `date_of_birth`, `address`, `diagnosis`, `status`, `notes`, `created_at`, `updated_at`) VALUES
(3, 11, 'Sample', 'Patient', 'patient@gmail.com', '09693052186', '2002-04-11', 'Iloilo', 'Kulang sa pag ibig', 'Active', 'Need immediate treatment!! This patient lacks self esteem and lack of sleep', '2025-04-11 02:40:28', '2025-04-11 02:40:28');

-- --------------------------------------------------------

--
-- Table structure for table `Reviews`
--

CREATE TABLE `Reviews` (
  `review_id` int(11) NOT NULL,
  `therapist_id` int(11) NOT NULL,
  `patient_id` int(11) NOT NULL,
  `rating` float NOT NULL,
  `comment` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ;

--
-- Triggers `Reviews`
--
DELIMITER $$
CREATE TRIGGER `after_review_delete` AFTER DELETE ON `Reviews` FOR EACH ROW BEGIN
    UPDATE Therapists
    SET rating = COALESCE((SELECT AVG(rating) FROM Reviews WHERE therapist_id = OLD.therapist_id), 0),
        review_count = (SELECT COUNT(*) FROM Reviews WHERE therapist_id = OLD.therapist_id)
    WHERE id = OLD.therapist_id;
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `after_review_insert` AFTER INSERT ON `Reviews` FOR EACH ROW BEGIN
    UPDATE Therapists
    SET rating = (SELECT AVG(rating) FROM Reviews WHERE therapist_id = NEW.therapist_id),
        review_count = (SELECT COUNT(*) FROM Reviews WHERE therapist_id = NEW.therapist_id)
    WHERE id = NEW.therapist_id;
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `after_review_update` AFTER UPDATE ON `Reviews` FOR EACH ROW BEGIN
    UPDATE Therapists
    SET rating = (SELECT AVG(rating) FROM Reviews WHERE therapist_id = NEW.therapist_id),
        review_count = (SELECT COUNT(*) FROM Reviews WHERE therapist_id = NEW.therapist_id)
    WHERE id = NEW.therapist_id;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `subscriptions`
--

CREATE TABLE `subscriptions` (
  `subscription_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `plan_type` enum('Free','Pro','Enterprise') DEFAULT 'Free',
  `start_date` date DEFAULT curdate(),
  `end_date` date DEFAULT NULL,
  `payment_status` enum('Pending','Completed','Failed') DEFAULT 'Pending',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `Therapists`
--

CREATE TABLE `Therapists` (
  `id` int(11) NOT NULL,
  `first_name` varchar(255) NOT NULL,
  `last_name` varchar(255) NOT NULL,
  `company_email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `profile_image` varchar(255) DEFAULT 'avatar-1.jpg',
  `bio` text DEFAULT NULL,
  `experience_years` int(11) DEFAULT 0,
  `specialties` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`specialties`)),
  `education` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`education`)),
  `languages` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`languages`)),
  `address` text DEFAULT NULL,
  `rating` float DEFAULT 0,
  `review_count` int(11) DEFAULT 0,
  `is_accepting_new_patients` tinyint(1) DEFAULT 1,
  `average_session_length` int(11) DEFAULT 60
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `Therapists`
--

INSERT INTO `Therapists` (`id`, `first_name`, `last_name`, `company_email`, `password`, `profile_image`, `bio`, `experience_years`, `specialties`, `education`, `languages`, `address`, `rating`, `review_count`, `is_accepting_new_patients`, `average_session_length`) VALUES
(10, 'Mariah', 'Yalong', 'Yalong@gmail.com', '$2b$12$jsQuPBFFg0x1cwPXoyJbgeefWq4usxclTKfArvi5tiuNiwlH8fvle', 'therapist_10_1744267485.jpg', 'Therapy expert', 10, '[\"Orthopedic Physical Therapy\", \"Neurological Physical Therapy\", \"Cardiovascular & Pulmonary Physical Therapy\", \"Pediatric Physical Therapy\", \"Geriatric Physical Therapy\", \"Sports Physical Therapy\", \"Women\'s Health Physical Therapy\", \"Manual Therapy\", \"Vestibular Rehabilitation\", \"Post-Surgical Rehabilitation\", \"Pain Management\"]', '[\"Harvard University\"]', '[\"English\", \"Spanish\", \"French\", \"German\", \"Italian\", \"Portuguese\"]', 'Antipolo', 5, 98, 1, 60),
(11, 'Selwyn', 'Jayme', 'jayme@gmail.com', '$2b$12$aiW6j9qcPt5285m7hNcLV.TOGceFyqysucrJGx1OwMNzk0sQbwpLi', 'therapist_11_1744291385.jpg', '', 0, '[]', '[]', '[]', '', 0, 0, 1, 60);

-- --------------------------------------------------------

--
-- Table structure for table `TreatmentPlanExercises`
--

CREATE TABLE `TreatmentPlanExercises` (
  `plan_exercise_id` int(11) NOT NULL,
  `plan_id` int(11) NOT NULL,
  `exercise_id` int(11) NOT NULL,
  `sets` int(11) DEFAULT 1,
  `repetitions` int(11) DEFAULT NULL,
  `frequency` varchar(100) DEFAULT NULL,
  `duration` int(11) DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `TreatmentPlans`
--

CREATE TABLE `TreatmentPlans` (
  `plan_id` int(11) NOT NULL,
  `patient_id` int(11) NOT NULL,
  `therapist_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `status` enum('Active','Completed','Cancelled') DEFAULT 'Active',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `profile_pic` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`user_id`, `username`, `email`, `password_hash`, `profile_pic`, `created_at`, `updated_at`) VALUES
(38, '111', '111@gmail.com', '$2b$12$CwEvo2MRR954ZXkJugnjfezcFDiPsV4k2wFD7ygWQJu1mgfou9Xom', NULL, '2025-04-10 22:57:28', '2025-04-10 22:57:28');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `Appointments`
--
ALTER TABLE `Appointments`
  ADD PRIMARY KEY (`appointment_id`),
  ADD KEY `patient_id` (`patient_id`),
  ADD KEY `therapist_id` (`therapist_id`);

--
-- Indexes for table `ExerciseCategories`
--
ALTER TABLE `ExerciseCategories`
  ADD PRIMARY KEY (`category_id`);

--
-- Indexes for table `Exercises`
--
ALTER TABLE `Exercises`
  ADD PRIMARY KEY (`exercise_id`),
  ADD KEY `therapist_id` (`therapist_id`),
  ADD KEY `category_id` (`category_id`);

--
-- Indexes for table `feedback`
--
ALTER TABLE `feedback`
  ADD PRIMARY KEY (`feedback_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `Messages`
--
ALTER TABLE `Messages`
  ADD PRIMARY KEY (`message_id`),
  ADD KEY `recipient_id` (`recipient_id`,`is_read`),
  ADD KEY `created_at` (`created_at`),
  ADD KEY `idx_messages_sender` (`sender_id`,`sender_type`),
  ADD KEY `idx_messages_recipient` (`recipient_id`,`recipient_type`),
  ADD KEY `idx_messages_read_status` (`is_read`);

--
-- Indexes for table `PatientExerciseProgress`
--
ALTER TABLE `PatientExerciseProgress`
  ADD PRIMARY KEY (`progress_id`),
  ADD KEY `patient_id` (`patient_id`),
  ADD KEY `plan_exercise_id` (`plan_exercise_id`);

--
-- Indexes for table `PatientMetrics`
--
ALTER TABLE `PatientMetrics`
  ADD PRIMARY KEY (`metric_id`),
  ADD KEY `patient_id` (`patient_id`),
  ADD KEY `therapist_id` (`therapist_id`);

--
-- Indexes for table `PatientNotes`
--
ALTER TABLE `PatientNotes`
  ADD PRIMARY KEY (`note_id`),
  ADD KEY `patient_id` (`patient_id`),
  ADD KEY `therapist_id` (`therapist_id`),
  ADD KEY `appointment_id` (`appointment_id`);

--
-- Indexes for table `Patients`
--
ALTER TABLE `Patients`
  ADD PRIMARY KEY (`patient_id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD KEY `therapist_id` (`therapist_id`);

--
-- Indexes for table `Reviews`
--
ALTER TABLE `Reviews`
  ADD PRIMARY KEY (`review_id`),
  ADD KEY `patient_id` (`patient_id`),
  ADD KEY `idx_review_therapist` (`therapist_id`);

--
-- Indexes for table `subscriptions`
--
ALTER TABLE `subscriptions`
  ADD PRIMARY KEY (`subscription_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `Therapists`
--
ALTER TABLE `Therapists`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `company_email` (`company_email`),
  ADD KEY `idx_therapist_rating` (`rating`);

--
-- Indexes for table `TreatmentPlanExercises`
--
ALTER TABLE `TreatmentPlanExercises`
  ADD PRIMARY KEY (`plan_exercise_id`),
  ADD KEY `plan_id` (`plan_id`),
  ADD KEY `exercise_id` (`exercise_id`);

--
-- Indexes for table `TreatmentPlans`
--
ALTER TABLE `TreatmentPlans`
  ADD PRIMARY KEY (`plan_id`),
  ADD KEY `patient_id` (`patient_id`),
  ADD KEY `therapist_id` (`therapist_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `Appointments`
--
ALTER TABLE `Appointments`
  MODIFY `appointment_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `ExerciseCategories`
--
ALTER TABLE `ExerciseCategories`
  MODIFY `category_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `Exercises`
--
ALTER TABLE `Exercises`
  MODIFY `exercise_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `feedback`
--
ALTER TABLE `feedback`
  MODIFY `feedback_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `Messages`
--
ALTER TABLE `Messages`
  MODIFY `message_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT for table `PatientExerciseProgress`
--
ALTER TABLE `PatientExerciseProgress`
  MODIFY `progress_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `PatientMetrics`
--
ALTER TABLE `PatientMetrics`
  MODIFY `metric_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `PatientNotes`
--
ALTER TABLE `PatientNotes`
  MODIFY `note_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `Patients`
--
ALTER TABLE `Patients`
  MODIFY `patient_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `Reviews`
--
ALTER TABLE `Reviews`
  MODIFY `review_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `subscriptions`
--
ALTER TABLE `subscriptions`
  MODIFY `subscription_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `Therapists`
--
ALTER TABLE `Therapists`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `TreatmentPlanExercises`
--
ALTER TABLE `TreatmentPlanExercises`
  MODIFY `plan_exercise_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `TreatmentPlans`
--
ALTER TABLE `TreatmentPlans`
  MODIFY `plan_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=40;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `Appointments`
--
ALTER TABLE `Appointments`
  ADD CONSTRAINT `Appointments_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `Patients` (`patient_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `Appointments_ibfk_2` FOREIGN KEY (`therapist_id`) REFERENCES `Therapists` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `Exercises`
--
ALTER TABLE `Exercises`
  ADD CONSTRAINT `Exercises_ibfk_1` FOREIGN KEY (`therapist_id`) REFERENCES `Therapists` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `Exercises_ibfk_2` FOREIGN KEY (`category_id`) REFERENCES `ExerciseCategories` (`category_id`) ON DELETE SET NULL;

--
-- Constraints for table `feedback`
--
ALTER TABLE `feedback`
  ADD CONSTRAINT `feedback_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `Messages`
--
ALTER TABLE `Messages`
  ADD CONSTRAINT `Messages_ibfk_1` FOREIGN KEY (`sender_id`) REFERENCES `Therapists` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `Messages_ibfk_2` FOREIGN KEY (`recipient_id`) REFERENCES `Therapists` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `PatientExerciseProgress`
--
ALTER TABLE `PatientExerciseProgress`
  ADD CONSTRAINT `PatientExerciseProgress_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `Patients` (`patient_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `PatientExerciseProgress_ibfk_2` FOREIGN KEY (`plan_exercise_id`) REFERENCES `TreatmentPlanExercises` (`plan_exercise_id`) ON DELETE CASCADE;

--
-- Constraints for table `PatientMetrics`
--
ALTER TABLE `PatientMetrics`
  ADD CONSTRAINT `PatientMetrics_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `Patients` (`patient_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `PatientMetrics_ibfk_2` FOREIGN KEY (`therapist_id`) REFERENCES `Therapists` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `PatientNotes`
--
ALTER TABLE `PatientNotes`
  ADD CONSTRAINT `PatientNotes_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `Patients` (`patient_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `PatientNotes_ibfk_2` FOREIGN KEY (`therapist_id`) REFERENCES `Therapists` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `PatientNotes_ibfk_3` FOREIGN KEY (`appointment_id`) REFERENCES `Appointments` (`appointment_id`) ON DELETE SET NULL;

--
-- Constraints for table `Patients`
--
ALTER TABLE `Patients`
  ADD CONSTRAINT `Patients_ibfk_1` FOREIGN KEY (`therapist_id`) REFERENCES `Therapists` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `Reviews`
--
ALTER TABLE `Reviews`
  ADD CONSTRAINT `Reviews_ibfk_1` FOREIGN KEY (`therapist_id`) REFERENCES `Therapists` (`id`),
  ADD CONSTRAINT `Reviews_ibfk_2` FOREIGN KEY (`patient_id`) REFERENCES `Patients` (`patient_id`);

--
-- Constraints for table `subscriptions`
--
ALTER TABLE `subscriptions`
  ADD CONSTRAINT `subscriptions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `TreatmentPlanExercises`
--
ALTER TABLE `TreatmentPlanExercises`
  ADD CONSTRAINT `TreatmentPlanExercises_ibfk_1` FOREIGN KEY (`plan_id`) REFERENCES `TreatmentPlans` (`plan_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `TreatmentPlanExercises_ibfk_2` FOREIGN KEY (`exercise_id`) REFERENCES `Exercises` (`exercise_id`) ON DELETE CASCADE;

--
-- Constraints for table `TreatmentPlans`
--
ALTER TABLE `TreatmentPlans`
  ADD CONSTRAINT `TreatmentPlans_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `Patients` (`patient_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `TreatmentPlans_ibfk_2` FOREIGN KEY (`therapist_id`) REFERENCES `Therapists` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
