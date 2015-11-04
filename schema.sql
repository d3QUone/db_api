SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

DROP SCHEMA IF EXISTS `forumdb`;
CREATE SCHEMA IF NOT EXISTS `forumdb` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `forumdb`;

-- -----------------------------------------------------
-- Table `forumdb`.`user`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `forumdb`.`user` ;

CREATE TABLE IF NOT EXISTS `forumdb`.`user` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(255) NULL,
  `email` VARCHAR(255) NOT NULL,
  `isAnonymous` TINYINT(1) UNSIGNED NULL DEFAULT 0,
  `about` TEXT NULL,
  `name` VARCHAR(255) NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY (`email`),
	UNIQUE KEY name_email (name, email))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `forumdb`.`forum`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `forumdb`.`forum` ;

CREATE TABLE IF NOT EXISTS `forumdb`.`forum` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(145) NOT NULL,
  `user` VARCHAR(45) NOT NULL,
  `short_name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`),
	UNIQUE KEY (`short_name`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `forumdb`.`thread`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `forumdb`.`thread` ;

CREATE TABLE IF NOT EXISTS `forumdb`.`thread` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(145) NOT NULL,
  `date` DATETIME NOT NULL,
  `message` TEXT NOT NULL,
  `forum` VARCHAR(45) NOT NULL,
  `user` VARCHAR(45) NOT NULL,
  `isDeleted` TINYINT NOT NULL DEFAULT 0,
  `isClosed` TINYINT NOT NULL DEFAULT 0,
  `slug` VARCHAR(65) NOT NULL,
  `likes` INT UNSIGNED NOT NULL DEFAULT 0,
  `dislikes` INT UNSIGNED NOT NULL DEFAULT 0,
  `points` INT NOT NULL DEFAULT 0,
  `posts` INT NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY (`title`),
	KEY (user))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `forumdb`.`post`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `forumdb`.`post` ;

CREATE TABLE IF NOT EXISTS `forumdb`.`post` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `message` TEXT NOT NULL,
  `date` DATETIME NOT NULL,
  `thread` INT UNSIGNED NOT NULL,
  `user` VARCHAR(45) NOT NULL,
  `parent` INT UNSIGNED NULL,
  `isApproved` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  `isDeleted` TINYINT NOT NULL DEFAULT 0,
  `isEdited` TINYINT NOT NULL DEFAULT 0,
  `isSpam` TINYINT NOT NULL DEFAULT 0,
  `isHighlighted` TINYINT NOT NULL DEFAULT 0,
  `forum` VARCHAR(45) NOT NULL,
  `likes` INT UNSIGNED NOT NULL DEFAULT 0,
  `dislikes` INT UNSIGNED NOT NULL DEFAULT 0,
  `points` INT NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_date` (`user`, `date`),
	KEY (`forum`),
	KEY `thread_date` (`thread`, `date`),
  INDEX `forum_user` (`forum`, `user`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `forumdb`.`subscription`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `forumdb`.`subscription` ;

CREATE TABLE IF NOT EXISTS `forumdb`.`subscription` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user` VARCHAR(45) NOT NULL,
  `thread` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `user_thread` (`user`, `thread`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `forumdb`.`follower`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `forumdb`.`follower` ;

CREATE TABLE IF NOT EXISTS `forumdb`.`follower` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `follower` VARCHAR(45) NOT NULL,
  `followee` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `main` (`follower`, `followee`))
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
