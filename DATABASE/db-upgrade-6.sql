ALTER TABLE `d2_user` CHANGE `ircauth` `irc_auth` LONGTEXT CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL; 
ALTER TABLE `d2_user` CHANGE `uploadauth` `upload_auth` LONGTEXT CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL; 
ALTER TABLE `d2_user` ADD `user_auth` LONGTEXT NOT NULL AFTER `upload_auth`; 