ALTER TABLE `d2_user` DROP `gender`, DROP `location`, DROP `occupation`, DROP `bio`, DROP `site`; 
ALTER TABLE `d2_user` ADD `bio` LONGTEXT NOT NULL AFTER `title`;
DROP TABLE `d2_session`;
DROP TABLE `d2_forums`;