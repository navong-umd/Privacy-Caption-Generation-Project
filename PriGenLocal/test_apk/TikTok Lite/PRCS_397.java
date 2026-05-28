/*Application Package Name: com.tiktok.lite.go
class PRCS_397 {
/**
com.ss.android.account.share.data.read.-;run()V
*/

    public final void run()
    {
        X.3qs v4_0 = this.f$0;
        android.content.Context v15 = this.f$1;
        String v7 = this.f$2;
        X.3qs v3_10 = v4_0.iterator();
        while (v3_10.hasNext()) {
            int v2_2 = ((X.3qq) v3_10.next());
            if (X.3sZ.LB(v15, v2_2.L)) {
                X.3qt.LCC.add(v2_2.L);
            }
        }
        java.util.Iterator v16 = v4_0.iterator();
        int v5 = 0;
        while (v16.hasNext()) {
            boolean v0_5 = ((X.3qq) v16.next());
            try {
                if (X.3sZ.LB(v15, v0_5.L)) {
                    if (X.3qt.L(v0_5.L)) {
                        v5 = 1;
                        X.3qs v3_0 = 0;
                        if (v0_5.LBL) {
                            String v1_51;
                            X.3qs v8_15 = android.accounts.AccountManager.get(X.3qt.L);
                            String v9_11 = v0_5.LCCII;
                            X.3qs v17_5 = new com.bytedance.helios.statichook.api.HeliosApiHook();
                            String v1_49 = new Object[1];
                            v1_49[0] = v9_11;
                            X.3qs v4_19 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "(Ljava/lang/String;)[Landroid/accounts/Account;", "dzBzEhEpEcvSUUUuTBbKZylIDzO5MvA7/D1DaU//QncYdl9tqB53KSdVB4xJPY4xw4V1/ARiAMTlq5I2gtw=");
                            Object[] v23_3 = v1_49;
                            String v1_50 = v17_5.preInvoke(102501, "android/accounts/AccountManager", "getAccountsByType", v8_15, v1_49, "android.accounts.Account[]", v4_19);
                            if (!v1_50.intercept) {
                                v1_51 = v8_15.getAccountsByType(v9_11);
                                v17_5.postInvoke(v1_51, 102501, "android/accounts/AccountManager", "getAccountsByType", v8_15, v23_3, v4_19, 1);
                            } else {
                                v17_5.postInvoke(0, 102501, "android/accounts/AccountManager", "getAccountsByType", v8_15, v23_3, v4_19, 0);
                                v1_51 = ((android.accounts.Account[]) v1_50.returnValue);
                            }
                            int v13_5 = v1_51.length;
                            X.3qs v4_20 = 0;
                            while (v4_20 < v13_5) {
                                String v9_1;
                                boolean v10_9 = v1_51[v4_20];
                                v4_20++;
                                X.3qs v17_8 = new com.bytedance.helios.statichook.api.HeliosApiHook();
                                String v9_12 = new Object[2];
                                v9_12[0] = v10_9;
                                v9_12[1] = v7;
                                com.bytedance.helios.statichook.api.ExtraInfo v12_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "(Landroid/accounts/Account;Ljava/lang/String;)Ljava/lang/String;", "dzBzEhEpEcvSUUUuTBbKZylIDzO5MvA7/D1DaU//QncYdl9tqB53KSdVB4xJPY4xw4V1/ARiAMTlq5I2gtw=");
                                Object[] v23_0 = v9_12;
                                String v9_0 = v17_8.preInvoke(110, "android/accounts/AccountManager", "getUserData", v8_15, v9_12, "java.lang.String", v12_1);
                                if (!v9_0.intercept) {
                                    v9_1 = v8_15.getUserData(v10_9, v7);
                                    v17_8.postInvoke(v9_1, 110, "android/accounts/AccountManager", "getUserData", v8_15, v23_0, v12_1, 1);
                                } else {
                                    v17_8.postInvoke(0, 110, "android/accounts/AccountManager", "getUserData", v8_15, v23_0, v12_1, 0);
                                    v9_1 = ((String) v9_0.returnValue);
                                }
                                if (!android.text.TextUtils.isEmpty(v9_1)) {
                                    X.3qs v4_1 = new X.3qs;
                                    v4_1(v0_5.L, 1, 0, 12, 0);
                                    v4_1.LCC = v7;
                                    v4_1.LC = 1;
                                    v4_1.LCCII = v9_1;
                                    v3_0 = v4_1;
                                    if (v3_0.LB) {
                                        X.3qt.L(v3_0);
                                        v0_5 = android.text.TextUtils.isEmpty(v3_0.LCCII);
                                        if (!v0_5) {
                                            return;
                                        }
                                    }
                                }
                            }
                            v3_0 = new X.3qs(v0_5.L, 0, "read form account failed", 1);
                        }
                        if (v0_5.LC) {
                            X.3qs v4_9;
                            X.3qs v4_6 = new StringBuilder("content://");
                            v4_6.append(v0_5.L);
                            v4_6.append(".SecShareProviderAuthority/sec_share/");
                            v4_6.append(v7);
                            v4_6.append("?aid=");
                            v4_6.append(v0_5.LB);
                            boolean v10_1 = android.net.Uri.parse(v4_6.toString());
                            int v22_3 = X.3qt.L.getContentResolver();
                            X.3qs v17_3 = new com.bytedance.helios.statichook.api.HeliosApiHook();
                            X.3qs v4_7 = new Object[5];
                            v4_7[0] = v10_1;
                            v4_7[1] = 0;
                            v4_7[2] = 0;
                            v4_7[3] = 0;
                            v4_7[4] = 0;
                            String v1_20 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "(Landroid/net/Uri;[Ljava/lang/String;Ljava/lang/String;[Ljava/lang/String;Ljava/lang/String;)Landroid/database/Cursor;", "dzBzEhEpEcvSUUUuTBbKZylIDzO5MvA7/D1DaU//QncYdl9tqB53KSdVB4xJPY4xw4V1/ARiAMTlq5I2gtw=");
                            Object[] v23_2 = v4_7;
                            X.3qs v4_8 = v17_3.preInvoke(240004, "android/content/ContentResolver", "query", v22_3, v4_7, "android.database.Cursor", v1_20);
                            if (!v4_8.intercept) {
                                v4_9 = v22_3.query(v10_1, 0, 0, 0, 0);
                                v17_3.postInvoke(v4_9, 240004, "android/content/ContentResolver", "query", v22_3, v23_2, v1_20, 1);
                            } else {
                                v17_3.postInvoke(0, 240004, "android/content/ContentResolver", "query", v22_3, v23_2, v1_20, 0);
                                v4_9 = ((android.database.Cursor) v4_8.returnValue);
                            }
                            X.3qs v8_5;
                            if (v4_9 == null) {
                                v8_5 = new X.3qs(v0_5.L, 0, "read form provider", 2);
                                if (v8_5.LB) {
                                    X.3qt.L(v8_5);
                                    v0_5 = android.text.TextUtils.isEmpty(v8_5.LCCII);
                                    if (!v0_5) {
                                        return;
                                    }
                                }
                            } else {
                                v4_9.moveToFirst();
                                X.3qs v4_12 = v4_9.getString(v4_9.getColumnIndex(v7));
                                v8_5 = new X.3qs(v0_5.L, 1, 0, 12, 0);
                                v8_5.LCC = v7;
                                v8_5.LC = 2;
                                v8_5.LCCII = v4_12;
                            }
                        }
                        if (!v0_5.LCC) {
                            if (v3_0 == null) {
                                v3_0 = new X.3qs;
                                v3_0(v0_5.L, 0, "have no valid query type", 8, 0);
                            }
                            X.3qt.L(v3_0);
                        } else {
                            X.3qt.LBL.post(new com.ss.android.account.share.data.read.-$$Lambda$d$3(v7, v0_5));
                        }
                    } else {
                        X.3qt.L(new X.3qs(v0_5.L, 0, "not support", 8, 0));
                    }
                } else {
                    X.3qt.L(new X.3qs(v0_5.L, 0, "no install", 8, 0));
                }
            } catch (X.3qs v8_14) {
                v8_14.printStackTrace();
                X.3qs v4_17 = new X.3qm();
                v4_17.L("share_sdk_read_data_err");
                v4_17.L("err_msg", v8_14.getMessage());
                v4_17.L("err_msg_stack", android.util.Log.getStackTraceString(v8_14));
                v4_17.L();
                X.3qt.L(new X.3qs(v0_5.L, 0, "read form provider", 2));
            }
        }
        if (v5 == 0) {
            X.3qt.L(new X.3qs("", 0, "no valid query pkg", 2));
        }
        return;
    }


}