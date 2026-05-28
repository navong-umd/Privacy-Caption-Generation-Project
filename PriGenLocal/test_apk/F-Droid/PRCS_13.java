/*Application Package Name: org.fdroid.fdroid
class PRCS_13 {
/**
org.fdroid.fdroid.net.ConnectivityMonitorService;getNetworkState(Landroid/content/Context;)I
*/

    public static int getNetworkState(android.content.Context p7)
    {
        int v7_2 = ((android.net.ConnectivityManager) androidx.core.content.ContextCompat.getSystemService(p7, android.net.ConnectivityManager));
        if (v7_2 != 0) {
            int v1_0 = v7_2.getActiveNetworkInfo();
            if ((v1_0 == 0) && (v7_2.getAllNetworks().length == 0)) {
                String v2_2 = java.net.NetworkInterface.getNetworkInterfaces();
                while (v2_2.hasMoreElements()) {
                    String v3_2 = ((java.net.NetworkInterface) v2_2.nextElement());
                    if ((v3_2.getDisplayName().contains("wlan0")) || ((v3_2.getDisplayName().contains("eth0")) || (v3_2.getDisplayName().contains("ap0")))) {
                        StringBuilder v4_6 = v3_2.getInetAddresses();
                        while (v4_6.hasMoreElements()) {
                            java.net.InetAddress v5_5 = ((java.net.InetAddress) v4_6.nextElement());
                            if (!v5_5.isLoopbackAddress()) {
                                if (!(v5_5 instanceof java.net.Inet6Address)) {
                                    StringBuilder v4_8 = new StringBuilder();
                                    v4_8.append("FLAG_NET_DEVICE_AP_WITHOUT_INTERNET: ");
                                    v4_8.append(v3_2.getDisplayName());
                                    v4_8.append(" ");
                                    v4_8.append(v5_5);
                                    android.util.Log.i("ConnectivityMonitorServ", v4_8.toString());
                                    return 3;
                                } else {
                                }
                            }
                        }
                    }
                }
            }
            if ((v1_0 != 0) && (v1_0.isConnected())) {
                int v0_2 = v1_0.getType();
                if ((v0_2 == 1) || (v0_2 == 9)) {
                    if (!androidx.core.net.ConnectivityManagerCompat.isActiveNetworkMetered(v7_2)) {
                        return 2;
                    } else {
                        return 1;
                    }
                } else {
                    return 1;
                }
            } else {
                return 0;
            }
        } else {
            return 0;
        }
    }

/**
org.fdroid.fdroid.work.RepoUpdateWorker;updateNow(Landroid/content/Context; J)V
*/

    public final void updateNow(android.content.Context p5, long p6)
    {
        kotlin.jvm.internal.Intrinsics.checkNotNullParameter(p5, "context");
        androidx.work.OneTimeWorkRequest$Builder v0_7 = org.fdroid.fdroid.work.RepoUpdateWorkerKt.access$getTAG$p();
        String v1_6 = new StringBuilder();
        v1_6.append("Update repo with ID ");
        v1_6.append(p6);
        v1_6.append(" now!");
        android.util.Log.i(v0_7, v1_6.toString());
        if ((org.fdroid.fdroid.FDroidApp.networkState <= 0) || (org.fdroid.fdroid.Preferences.get().isOnDemandDownloadAllowed())) {
            if (org.fdroid.fdroid.net.ConnectivityMonitorService.getNetworkState(p5) != 0) {
                androidx.work.OneTimeWorkRequest$Builder v0_9 = ((androidx.work.OneTimeWorkRequest$Builder) new androidx.work.OneTimeWorkRequest$Builder(org.fdroid.fdroid.work.RepoUpdateWorker).setExpedited(androidx.work.OutOfQuotaPolicy.RUN_AS_NON_EXPEDITED_WORK_REQUEST));
                if (p6 >= 0) {
                    String v1_2 = new kotlin.Pair[1];
                    v1_2[0] = kotlin.TuplesKt.to("repoId", Long.valueOf(p6));
                    androidx.work.OneTimeWorkRequest v6_4 = new androidx.work.Data$Builder();
                    String v7_1 = v1_2[0];
                    v6_4.put(((String) v7_1.getFirst()), v7_1.getSecond());
                    androidx.work.OneTimeWorkRequest v6_5 = v6_4.build();
                    kotlin.jvm.internal.Intrinsics.checkNotNullExpressionValue(v6_5, "dataBuilder.build()");
                    v0_9.setInputData(v6_5);
                }
                androidx.work.WorkManager.getInstance(p5).enqueue(((androidx.work.OneTimeWorkRequest) v0_9.build()));
                return;
            } else {
                android.widget.Toast.makeText(p5, org.fdroid.fdroid.R$string.warning_no_internet, 1).show();
                return;
            }
        } else {
            android.widget.Toast.makeText(p5, org.fdroid.fdroid.R$string.updates_disabled_by_settings, 1).show();
            return;
        }
    }

/**
org.fdroid.fdroid.views.repos.AddRepoActivity;emit(Lorg/fdroid/repo/AddRepoState; Lkotlin/coroutines/Continuation;)Ljava/lang/Object;
*/

    public final Object emit(org.fdroid.repo.AddRepoState p4, kotlin.coroutines.Continuation p5)
    {
        if ((p4 instanceof org.fdroid.repo.Added)) {
            long v0_3 = this.this$0.getApplicationContext();
            kotlin.jvm.internal.Intrinsics.checkNotNullExpressionValue(v0_3, "getApplicationContext(...)");
            org.fdroid.fdroid.work.RepoUpdateWorker.Companion.updateNow(v0_3, ((org.fdroid.repo.Added) p4).getRepo().getRepoId());
            android.content.Intent v5_2 = new android.content.Intent(this.this$0, org.fdroid.fdroid.views.apps.AppListActivity);
            v5_2.putExtra("org.fdroid.fdroid.views.apps.AppListActivity.REPO_ID", ((org.fdroid.repo.Added) p4).getRepo().getRepoId());
            this.this$0.startActivity(v5_2);
            this.this$0.finish();
        }
        return kotlin.Unit.INSTANCE;
    }


}