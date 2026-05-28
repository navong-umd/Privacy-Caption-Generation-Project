/*Application Package Name: com.tiktok.lite.go
class PRCS_179 {
/**
X.3Oy;L(Landroid/net/ConnectivityManager;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo L(android.net.ConnectivityManager p18)
    {
        try {
            com.bytedance.helios.statichook.api.HeliosApiHook v3_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
            Object[] v9 = new Object[0];
            com.bytedance.helios.statichook.api.ExtraInfo v10_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()Landroid/net/NetworkInfo;", "dzBzEgU1UM3QUBkgSxaWaaw9Bz14/yzxe1dYm0ZJPLqwOID9zPVdd3eEmUDB28ad");
            com.bytedance.helios.statichook.api.Result v1_0 = v3_1.preInvoke(183, "android/net/ConnectivityManager", "getActiveNetworkInfo", p18, v9, "android.net.NetworkInfo", v10_1);
        } catch (android.net.NetworkInfo v0_3) {
            v0_3.printStackTrace();
            return X.1Mw.L();
        }
        if (!v1_0.intercept) {
            android.net.NetworkInfo v4_0 = p18.getActiveNetworkInfo();
            v3_1.postInvoke(v4_0, 183, "android/net/ConnectivityManager", "getActiveNetworkInfo", p18, v9, v10_1, 1);
            return v4_0;
        } else {
            v3_1.postInvoke(0, 183, "android/net/ConnectivityManager", "getActiveNetworkInfo", p18, v9, v10_1, 0);
            return ((android.net.NetworkInfo) v1_0.returnValue);
        }
    }

/**
X.3Oy;LB()Z
*/

    public final boolean LB()
    {
        this.LFFLLL();
        android.net.ConnectivityManager v3_1 = ((android.net.ConnectivityManager) this.LIIII.L.getSystemService("connectivity"));
        android.net.NetworkInfo v4 = 0;
        if (v3_1 != null) {
            try {
                System.nanoTime();
            } catch (Exception) {
                if (v4 != null) {
                    if (v4.isConnected()) {
                        return 1;
                    }
                }
            }
            if (X.5uL.L()) {
                if ((X.75K.L()) || (X.5uK.LBL())) {
                    if (X.5uV.L()) {
                        if ((X.5uC.L == null) || ((!X.5uC.L.isConnected()) || (!X.5uC.L.isAvailable()))) {
                            X.5uC.L = X.3Oy.L(v3_1);
                            v4 = X.5uC.L;
                        } else {
                            if (X.5uO.L) {
                                X.5uL.L("cm_net_info", X.3Oy.L(v3_1).toString(), X.5uC.L.toString());
                            }
                            v4 = X.5uC.L;
                        }
                    } else {
                        X.5uC.L = 0;
                        v4 = X.3Oy.L(v3_1);
                    }
                } else {
                    v4 = X.3Oy.L(v3_1);
                }
            } else {
                v4 = X.3Oy.L(v3_1);
            }
        }
        return 0;
    }

/**
X.3RZ;L(I Ljava/lang/Throwable; [B)V
*/

    public final void L(int p15, Throwable p16, byte[] p17)
    {
        X.3Rs v9_0 = p17;
        this.ah_().ac_();
        this.LFFLLL();
        try {
            if (p17 == null) {
                v9_0 = new byte[0];
            }
        } catch (String v0_19) {
            this.LIIIII = 0;
            this.LII();
            throw v0_19;
        }
        android.database.sqlite.SQLiteException v5_3 = this.LIIIL;
        java.util.Objects.requireNonNull(v5_3, "null reference");
        this.LIIIL = 0;
        if (p15 == 200) {
            if (p16 != null) {
                this.ag_().LFFFF.L("Network upload failed. Will retry later. code, error", Integer.valueOf(p15), p16);
                this.LC.LC.L(this.ae_().L());
                if ((p15 == 503) || (p15 == 429)) {
                    this.LC.LB.L(this.ae_().L());
                }
                X.3Oo v4_8 = this.L;
                X.3RZ.L(v4_8);
                v4_8.ac_();
                v4_8.LFFLLL();
                X.3D5.L(v5_3);
                X.3D5.L(v5_3.size());
                if (X.3Rs.LI(v4_8)) {
                    String v2_28 = android.text.TextUtils.join(",", v5_3);
                    X.3Oo v1_6 = new StringBuilder();
                    v1_6.append("(");
                    v1_6.append(v2_28);
                    v1_6.append(")");
                    Long v7_3 = v1_6.toString();
                    X.3Oo v1_8 = new StringBuilder();
                    v1_8.append("SELECT COUNT(1) FROM queue WHERE rowid IN ");
                    v1_8.append(v7_3);
                    v1_8.append(" AND retry_count =  2147483647 LIMIT 1");
                    if (X.3Rs.LB(v4_8, v1_8.toString(), 0) > 0) {
                        v4_8.LIIII.ag_().LCCII.L("The number of upload retries exceeds the limit. Will remain unchanged.");
                    }
                    String v2_29 = v4_8.LC();
                    X.3Oo v1_13 = new StringBuilder();
                    v1_13.append("UPDATE queue SET retry_count = IFNULL(retry_count, 0) + 1 WHERE rowid IN ");
                    v1_13.append(v7_3);
                    v1_13.append(" AND (retry_count IS NULL OR retry_count < 2147483647)");
                    v2_29.execSQL(v1_13.toString());
                }
                this.LFI();
            } else {
                try {
                    this.LC.LBL.L(this.ae_().L());
                    this.LC.LC.L(0);
                    this.LFI();
                    this.ag_().LFFFF.L("Successful upload. Got network response. code, size", Integer.valueOf(p15), Integer.valueOf(v9_0.length));
                    String v2_6 = this.L;
                    X.3RZ.L(v2_6);
                    v2_6.LCCII();
                } catch (String v2_23) {
                    this.ag_().LBL.L("Database error while trying to delete uploaded bundles", v2_23);
                    this.LIII = this.ae_().LB();
                    this.ag_().LFFFF.L("Disable upload, time", Long.valueOf(this.LIII));
                }
                java.util.Iterator v13 = v5_3.iterator();
                while (v13.hasNext()) {
                    Long v7_2 = ((Long) v13.next());
                    try {
                        X.3Rs v9_1 = this.L;
                        X.3RZ.L(v9_1);
                        long v11 = v7_2.longValue();
                        v9_1.ac_();
                        v9_1.LFFLLL();
                        android.database.sqlite.SQLiteDatabase v10 = v9_1.LC();
                        android.database.sqlite.SQLiteException v5_0 = new String[1];
                        v5_0[0] = String.valueOf(v11);
                        try {
                            if (v10.delete("queue", "rowid=?", v5_0) != 1) {
                                throw new android.database.sqlite.SQLiteException("Deleted fewer rows from queue than expected");
                            }
                        } catch (android.database.sqlite.SQLiteException v5_1) {
                            v9_1.LIIII.ag_().LBL.L("Failed to delete a bundle in a queue table", v5_1);
                            throw v5_1;
                        }
                    } catch (X.3Oo v4_6) {
                        String v2_21 = this.LIIILL;
                        if (v2_21 != null) {
                            if (v2_21.contains(v7_2)) {
                            }
                        }
                        throw v4_6;
                    }
                }
                String v2_8 = this.L;
                X.3RZ.L(v2_8);
                v2_8.LF();
                String v2_9 = this.L;
                X.3RZ.L(v2_9);
                v2_9.LCI();
                this.LIIILL = 0;
                String v2_10 = this.LFFFF;
                X.3RZ.L(v2_10);
                if ((!v2_10.LB()) || (!this.LIII())) {
                    this.LIIJILLL = -1;
                    this.LFI();
                } else {
                    this.LFLL();
                }
                this.LIII = 0;
            }
        } else {
            if (p15 != 204) {
            } else {
                p15 = 204;
            }
        }
        this.LIIIII = 0;
        this.LII();
        return;
    }


}