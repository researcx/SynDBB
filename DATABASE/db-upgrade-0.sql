-- phpMyAdmin SQL Dump
-- version 5.0.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Oct 08, 2020 at 09:42 PM
-- Server version: 10.4.11-MariaDB
-- PHP Version: 7.4.3

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";

--
-- Database: `cyndi`
--

-- --------------------------------------------------------

--
-- Table structure for table `d2_activity`
--

DROP TABLE IF EXISTS `d2_activity`;
CREATE TABLE `d2_activity` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `time` int(11) DEFAULT NULL,
  `content` longtext DEFAULT NULL,
  `replyto` int(11) DEFAULT NULL,
  `replyToPost` int(11) DEFAULT NULL,
  `title` longtext DEFAULT NULL,
  `category` int(11) DEFAULT NULL,
  `reply_time` int(11) DEFAULT NULL,
  `reply_count` int(11) DEFAULT NULL,
  `rating` int(11) NOT NULL,
  `post_icon` int(11) NOT NULL,
  `anonymous` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `d2_bans`
--

DROP TABLE IF EXISTS `d2_bans`;
CREATE TABLE `d2_bans` (
  `id` int(11) NOT NULL,
  `banned_id` int(11) DEFAULT NULL,
  `reason` longtext DEFAULT NULL,
  `length` int(11) DEFAULT NULL,
  `time` int(11) DEFAULT NULL,
  `expires` int(11) DEFAULT NULL,
  `post` int(11) DEFAULT NULL,
  `banner` int(11) DEFAULT NULL,
  `display` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `d2_channels`
--

DROP TABLE IF EXISTS `d2_channels`;
CREATE TABLE `d2_channels` (
  `id` int(11) NOT NULL,
  `name` longtext DEFAULT NULL,
  `short_name` longtext DEFAULT NULL,
  `description` longtext DEFAULT NULL,
  `chat_url` longtext DEFAULT NULL,
  `nsfw` int(11) DEFAULT NULL,
  `owned_by` int(11) DEFAULT NULL,
  `approved` int(11) DEFAULT NULL,
  `auth` int(11) DEFAULT NULL,
  `anon` int(11) DEFAULT NULL,
  `user_list` longtext NOT NULL,
  `mod_list` longtext NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `d2_channels`
--

INSERT INTO `d2_channels` (`id`, `name`, `short_name`, `description`, `chat_url`, `nsfw`, `owned_by`, `approved`, `auth`, `anon`, `user_list`, `mod_list`) VALUES
(1, 'General Discussion', 'general', '', 'https://d2k5.com/chat/', 0, 0, 1, 1, 1, '', ''),
(2, 'Hardware and Software', 'tech', '', 'https://d2k5.com/chat/', 0, 0, 1, 0, 1, '', ''),
(3, 'Media', 'media', '', 'https://d2k5.com/chat/', 0, 0, 1, 0, 1, '', ''),
(4, 'Lewd', 'lewd', 'All types of lewd content', NULL, 1, 0, 1, 1, 1, '', '');

-- --------------------------------------------------------

--
-- Table structure for table `d2_invites`
--

DROP TABLE IF EXISTS `d2_invites`;
CREATE TABLE `d2_invites` (
  `id` int(11) NOT NULL,
  `code` longtext DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `used_by` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `d2_ip`
--

DROP TABLE IF EXISTS `d2_ip`;
CREATE TABLE `d2_ip` (
  `id` int(11) NOT NULL,
  `ip` longtext DEFAULT NULL,
  `useragent` longtext NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `time` int(11) DEFAULT NULL,
  `login` int(11) DEFAULT NULL,
  `page` text DEFAULT NULL,
  `sessionid` longtext DEFAULT NULL,
  `iphash` longtext DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `d2_ip`
--

INSERT INTO `d2_ip` (`id`, `ip`, `useragent`, `user_id`, `time`, `login`, `page`, `sessionid`, `iphash`) VALUES
(1, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0', 1, 1602186035, 1, '/', 'c95498a0-099d-11eb-955b-ec55f9f44628', 'ae79184c70');

-- --------------------------------------------------------

--
-- Table structure for table `d2_paste`
--

DROP TABLE IF EXISTS `d2_paste`;
CREATE TABLE `d2_paste` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `paste_id` longtext DEFAULT NULL,
  `time` int(11) DEFAULT NULL,
  `content` longtext DEFAULT NULL,
  `title` longtext DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `d2_post_ratings`
--

DROP TABLE IF EXISTS `d2_post_ratings`;
CREATE TABLE `d2_post_ratings` (
  `id` int(11) NOT NULL,
  `post_id` int(11) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `type` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `d2_quotes`
--

DROP TABLE IF EXISTS `d2_quotes`;
CREATE TABLE `d2_quotes` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `time` int(11) DEFAULT NULL,
  `content` longtext DEFAULT NULL,
  `approved` int(11) DEFAULT NULL,
  `rating` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `d2_quote_ratings`
--

DROP TABLE IF EXISTS `d2_quote_ratings`;
CREATE TABLE `d2_quote_ratings` (
  `id` int(11) NOT NULL,
  `quote_id` int(11) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `type` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `d2_requests`
--

DROP TABLE IF EXISTS `d2_requests`;
CREATE TABLE `d2_requests` (
  `id` int(11) NOT NULL,
  `username` longtext DEFAULT NULL,
  `email` longtext DEFAULT NULL,
  `reason` longtext DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `d2_session`
--

DROP TABLE IF EXISTS `d2_session`;
CREATE TABLE `d2_session` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `sessionid` longtext DEFAULT NULL,
  `time` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `d2_session`
--

INSERT INTO `d2_session` (`id`, `user_id`, `sessionid`, `time`) VALUES
(1, 1, 'b749850c-877f-11e7-a9ac-b2dd0ebc51d2', 1503436826);

-- --------------------------------------------------------

--
-- Table structure for table `d2_user`
--

DROP TABLE IF EXISTS `d2_user`;
CREATE TABLE `d2_user` (
  `user_id` int(11) NOT NULL,
  `username` longtext NOT NULL,
  `token` longtext NOT NULL,
  `title` longtext NOT NULL,
  `status` longtext NOT NULL,
  `status_time` int(11) NOT NULL,
  `rank` int(11) NOT NULL,
  `gender` longtext NOT NULL,
  `location` longtext NOT NULL,
  `occupation` longtext NOT NULL,
  `bio` longtext NOT NULL,
  `site` longtext NOT NULL,
  `avatar_date` int(11) NOT NULL,
  `password` longtext NOT NULL,
  `post_count` int(11) NOT NULL,
  `line_count` int(11) NOT NULL,
  `word_count` int(11) NOT NULL,
  `profanity_count` int(11) NOT NULL,
  `karma_positive` int(11) NOT NULL,
  `karma_negative` int(11) NOT NULL,
  `points` int(11) NOT NULL,
  `join_date` int(11) NOT NULL,
  `last_login` int(11) NOT NULL,
  `last_activity` int(11) NOT NULL,
  `ircauth` longtext NOT NULL,
  `uploadauth` longtext NOT NULL,
  `upload_url` longtext NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `d2_user`
--

INSERT INTO `d2_user` (`user_id`, `username`, `token`, `title`, `status`, `status_time`, `rank`, `gender`, `location`, `occupation`, `bio`, `site`, `avatar_date`, `password`, `post_count`, `line_count`, `word_count`, `profanity_count`, `karma_positive`, `karma_negative`, `points`, `join_date`, `last_login`, `last_activity`, `ircauth`, `uploadauth`, `upload_url`) VALUES
(1, 'admin', '', 'Administrator', 'yes yes', 1602180753, 999, '', '', '', '', '', 1602122276, '7dca68a83668802fdddd9a01acb301028271f8820dce3634f92c803a789d8706', -17, 43986, 216262, 14063, 80, 1, 483, 1026345600, 1503436826, 1602186035, '', '', 'local');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `d2_activity`
--
ALTER TABLE `d2_activity`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `d2_bans`
--
ALTER TABLE `d2_bans`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `d2_channels`
--
ALTER TABLE `d2_channels`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `d2_invites`
--
ALTER TABLE `d2_invites`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `d2_ip`
--
ALTER TABLE `d2_ip`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `d2_paste`
--
ALTER TABLE `d2_paste`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `d2_post_ratings`
--
ALTER TABLE `d2_post_ratings`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `d2_quotes`
--
ALTER TABLE `d2_quotes`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `d2_quote_ratings`
--
ALTER TABLE `d2_quote_ratings`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `d2_requests`
--
ALTER TABLE `d2_requests`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `d2_session`
--
ALTER TABLE `d2_session`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `d2_user`
--
ALTER TABLE `d2_user`
  ADD PRIMARY KEY (`user_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `d2_activity`
--
ALTER TABLE `d2_activity`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;

--
-- AUTO_INCREMENT for table `d2_bans`
--
ALTER TABLE `d2_bans`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;

--
-- AUTO_INCREMENT for table `d2_channels`
--
ALTER TABLE `d2_channels`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `d2_invites`
--
ALTER TABLE `d2_invites`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;

--
-- AUTO_INCREMENT for table `d2_ip`
--
ALTER TABLE `d2_ip`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `d2_paste`
--
ALTER TABLE `d2_paste`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;

--
-- AUTO_INCREMENT for table `d2_post_ratings`
--
ALTER TABLE `d2_post_ratings`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;

--
-- AUTO_INCREMENT for table `d2_quotes`
--
ALTER TABLE `d2_quotes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;

--
-- AUTO_INCREMENT for table `d2_quote_ratings`
--
ALTER TABLE `d2_quote_ratings`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;

--
-- AUTO_INCREMENT for table `d2_requests`
--
ALTER TABLE `d2_requests`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;

--
-- AUTO_INCREMENT for table `d2_session`
--
ALTER TABLE `d2_session`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `d2_user`
--
ALTER TABLE `d2_user`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;
COMMIT;
