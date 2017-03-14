bin_SCRIPTS = yterm

yterm: yterm.in
	@$(MKDIR_P) bin
	$(AM_V_GEN)$(SED)                       \
		-e s!\@localedir\@!$(localedir)!    \ 
		-e s!\@pythondir\@!$(pythondir)!    \
		-e s!\@PYTHON\@!$(PYTHON)!          \
		< $< > $@
	@chmod a+x $@

BUILD_SOURCES = $(bin_SCRIPTS)
EXTRA_DIST = yterm.in

-include $(top_srcdir)/git.mk
