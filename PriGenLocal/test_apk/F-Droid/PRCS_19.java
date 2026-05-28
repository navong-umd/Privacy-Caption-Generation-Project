/*Application Package Name: org.fdroid.fdroid
class PRCS_19 {
/**
org.fdroid.fdroid.Preferences;setDefaultForDataOnlyConnection(Landroid/content/Context;)V
*/

    void setDefaultForDataOnlyConnection(android.content.Context p3)
    {
        android.content.SharedPreferences$Editor v3_7 = ((android.net.ConnectivityManager) androidx.core.content.ContextCompat.getSystemService(p3, android.net.ConnectivityManager));
        if (v3_7 != null) {
            String v0_4 = v3_7.getActiveNetworkInfo();
            if ((v0_4 != null) && ((v0_4.isConnectedOrConnecting()) && ((v0_4.getType() == 0) && (!v3_7.getNetworkInfo(1).isConnectedOrConnecting())))) {
                this.preferences.edit().putInt("overData", 2).apply();
            }
            return;
        } else {
            return;
        }
    }

/**
org.fdroid.fdroid.FDroidApp;onCreate()V
*/

    public void onCreate()
    {
        super.onCreate();
        org.fdroid.fdroid.FDroidApp.instance = this;
        org.fdroid.fdroid.Preferences.setup(this);
        org.fdroid.fdroid.Languages.setLanguage(this);
        android.content.SharedPreferences$Editor v0_15 = org.fdroid.fdroid.Preferences.get();
        if (v0_15.promptToSendCrashReports()) {
            String v4_1 = new Object[2];
            v4_1[0] = "org.fdroid.fdroid";
            v4_1[1] = "1.21.1";
            String v1_19 = String.format(java.util.Locale.ENGLISH, "%s %s: Crash Report", v4_1);
            String v4_11 = new org.acra.config.CoreConfigurationBuilder();
            long v5_8 = new org.acra.ReportField[13];
            v5_8[0] = org.acra.ReportField.USER_COMMENT;
            v5_8[1] = org.acra.ReportField.PACKAGE_NAME;
            v5_8[2] = org.acra.ReportField.APP_VERSION_NAME;
            v5_8[3] = org.acra.ReportField.ANDROID_VERSION;
            v5_8[4] = org.acra.ReportField.PRODUCT;
            v5_8[5] = org.acra.ReportField.BRAND;
            v5_8[6] = org.acra.ReportField.PHONE_MODEL;
            v5_8[7] = org.acra.ReportField.DISPLAY;
            v5_8[8] = org.acra.ReportField.TOTAL_MEM_SIZE;
            v5_8[9] = org.acra.ReportField.AVAILABLE_MEM_SIZE;
            v5_8[10] = org.acra.ReportField.CUSTOM_DATA;
            v5_8[11] = org.acra.ReportField.STACK_TRACE_HASH;
            v5_8[12] = org.acra.ReportField.STACK_TRACE;
            String v4_12 = v4_11.withReportContent(v5_8);
            android.content.SharedPreferences v3_11 = new org.acra.config.Configuration[2];
            v3_11[0] = new org.acra.config.MailSenderConfigurationBuilder().withMailTo("reports@f-droid.org").withReportFileName("ACRA-report.stacktrace.json").withSubject(v1_19).build();
            v3_11[1] = new org.acra.config.DialogConfigurationBuilder().withResTheme(Integer.valueOf(org.fdroid.fdroid.R$style.Theme_App)).withTitle(this.getString(org.fdroid.fdroid.R$string.crash_dialog_title)).withText(this.getString(org.fdroid.fdroid.R$string.crash_dialog_text)).withCommentPrompt(this.getString(org.fdroid.fdroid.R$string.crash_dialog_comment_prompt)).build();
            org.acra.ACRA.init(this, v4_12.withPluginConfigurations(v3_11));
            if ((this.isAcraProcess()) || (org.fdroid.fdroid.panic.HidingManager.isHidden(this))) {
                return;
            }
        }
        this.registerReceiver(new org.fdroid.fdroid.receiver.DeviceStorageReceiver(), new android.content.IntentFilter("android.intent.action.DEVICE_STORAGE_LOW"));
        org.fdroid.fdroid.nearby.WifiStateChangeService.registerReceiver(this);
        org.fdroid.fdroid.FDroidApp.applyTheme();
        org.fdroid.fdroid.FDroidApp.configureProxy(v0_15);
        v0_15.registerUnstableUpdatesChangeListener(new org.fdroid.fdroid.FDroidApp$$ExternalSyntheticLambda2(this));
        org.fdroid.fdroid.work.CleanCacheWorker.schedule(this);
        org.fdroid.fdroid.FDroidApp.sessionInstallManager = new org.fdroid.fdroid.installer.SessionInstallManager(this.getApplicationContext());
        this.notificationHelper = new org.fdroid.fdroid.NotificationHelper(this.getApplicationContext());
        if (v0_15.isIndexNeverUpdated()) {
            v0_15.setDefaultForDataOnlyConnection(this);
        }
        org.fdroid.fdroid.FDroidApp.networkState = org.fdroid.fdroid.net.ConnectivityMonitorService.getNetworkState(this);
        org.fdroid.fdroid.net.ConnectivityMonitorService.registerAndStart(this);
        org.fdroid.fdroid.work.RepoUpdateWorker.scheduleOrCancel(this.getApplicationContext());
        org.fdroid.fdroid.FDroidApp.initWifiSettings();
        org.fdroid.fdroid.nearby.WifiStateChangeService.start(this, 0);
        v0_15.registerLocalRepoHttpsListeners(new org.fdroid.fdroid.FDroidApp$$ExternalSyntheticLambda3(this));
        if (v0_15.isKeepingInstallHistory()) {
            org.fdroid.fdroid.installer.InstallHistoryService.register(this);
        }
        android.content.SharedPreferences v3_9 = this.getString(org.fdroid.fdroid.R$string.install_history_reader_packageName);
        if (!android.text.TextUtils.equals(v3_9, this.getString(org.fdroid.fdroid.R$string.install_history_reader_packageName_UNSET))) {
            this.grantUriPermission(v3_9, org.fdroid.fdroid.installer.InstallHistoryService.LOG_URI, 67);
        }
        android.content.SharedPreferences v3_10 = this.getAtStartTimeSharedPreferences();
        String v4_6 = android.os.Build$VERSION.SDK_INT;
        if (v4_6 != v3_10.getInt("build-version", v4_6)) {
            org.fdroid.fdroid.Utils.runOffUiThread(new org.fdroid.fdroid.FDroidApp$$ExternalSyntheticLambda4(this), new org.fdroid.fdroid.FDroidApp$$ExternalSyntheticLambda5(this));
        }
        v3_10.edit().putInt("build-version", v4_6).apply();
        if (!v0_15.isIndexNeverUpdated()) {
            this.updateLanguagesIfNecessary();
        }
        if (!v0_15.sendVersionAndUUIDToServers()) {
            v3_10.edit().remove("http-downloader-query-string").apply();
        } else {
            org.fdroid.fdroid.FDroidApp.queryString = v3_10.getString("http-downloader-query-string", 0);
            if (org.fdroid.fdroid.FDroidApp.queryString == null) {
                android.content.SharedPreferences$Editor v0_5 = java.util.UUID.randomUUID();
                String v1_18 = java.nio.ByteBuffer.allocate(16);
                v1_18.putLong(v0_5.getMostSignificantBits());
                v1_18.putLong(v0_5.getLeastSignificantBits());
                android.content.SharedPreferences$Editor v0_7 = android.util.Base64.encodeToString(v1_18.array(), 11);
                String v1_21 = new StringBuilder("id=");
                v1_21.append(v0_7);
                android.content.SharedPreferences$Editor v0_9 = android.net.Uri.encode(org.fdroid.fdroid.Utils.getVersionName(this));
                if (v0_9 != null) {
                    v1_21.append("&client_version=");
                    v1_21.append(v0_9);
                }
                org.fdroid.fdroid.FDroidApp.queryString = v1_21.toString();
                v3_10.edit().putString("http-downloader-query-string", org.fdroid.fdroid.FDroidApp.queryString).apply();
            }
        }
        if (org.fdroid.fdroid.Preferences.get().isScanRemovableStorageEnabled()) {
            org.fdroid.fdroid.nearby.SDCardScannerService.scan(this);
        }
        return;
    }


}