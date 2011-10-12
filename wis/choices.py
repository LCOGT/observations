STATUS_CHOICES = (
('active','Active'),
('suspended','Suspended'),
('pending','Pending'),
('rejected','Rejected'),
('deleted','Removed'),
('applied','Applied'),
)

statuschoices = {
'active':'Active',
'suspended':'Suspended',
'pending':'Pending',
'rejected':'Rejected',
'deleted':'Removed',
'applied':'Applied',
}

STATE_CHOICES = (
('Y','Yes'),
('N','No'),
)

SCOPE_CHOICES = (
(1,'Faulkes Telescope North'),
(2, 'Faulkes Telescope South'),
)

USER_TYPES = (
('S','School'),
('A','Astronomical Society'),
('C','Community group'),
('G','Regional Centre'),
('U','Unknown'),
('E','Education'),
('M','Marketing'),
('D','Administrator'),
('R','Research'),
('P','AstroSoc/School Ptnr'),
('L','LCOGT staff'),
('Z','Local to site user'),
)

usertypes = {
'S':'School',
'A':'Astronomical Society',
'C':'Community group',
'G':'Regional Centre',
'U':'Unknown',
'E':'Education',
'M':'Marketing',
'D':'Administrator',
'R':'Research',
'P':'AstroSoc/School Ptnr',
'L':'LCOGT staff',
'Z':'Local to site user',
}

FOOTER_CHOICES = (
(1,'FT team'),
(2,'LCOGT education'),
)

email_footer = {
1 : ' \nWarm regards,\nFT team\n--\nFaulkes Telescope Project\nhttp://faulkes-telescope.com',
2 : ' \nWarm regards,\nEducation team\n--\nLas Cumbres Observatory Global Telescope\nhttp://lcogt.net'
}
email_sender = {
1 : 'support@faulkes-telescope.com',
2 : 'no-reply@lcogt.net',
}

TEL_TWITTER = (
('faulkestel','naturalhistory'),
('oggftn','darkskies0'),
('cojfts','darkskies0'),
)