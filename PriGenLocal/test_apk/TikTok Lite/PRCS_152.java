/*Application Package Name: com.tiktok.lite.go
class PRCS_152 {
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
X.3RZ;LFLL()V
*/

    public final void LFLL()
    {
        void v8 = this;
        this.ah_().ac_();
        this.LFFLLL();
        X.3Oy v10_5 = 1;
        this.LIIIIZ = 1;
        X.3Ov v9_10 = 0;
        try {
            X.3Ov v0_14 = this.LCC.LFFLLL().LBL;
        } catch (X.3PP v1_5) {
            v8.LIIIIZ = 0;
            v8.LII();
            throw v1_5;
        }
        if (v0_14 != null) {
            if (!v0_14.booleanValue()) {
                if (this.LIII <= 0) {
                    this.ah_().ac_();
                    if (this.LIIIL == null) {
                        X.3Ov v0_28 = this.LFFFF;
                        X.3RZ.L(v0_28);
                        if (v0_28.LB()) {
                            X.3Ov v0_31 = this.ae_().L();
                            X.3Oy v7_0 = 0;
                            String v6_0 = this.L().LB(0, X.3Oc.LIILZZ);
                            this.L();
                            int v4_39 = X.3Pl.LD();
                            X.3Ir v5_2 = 0;
                            while ((v5_2 < v6_0) && (this.L((v0_31 - v4_39)))) {
                                v5_2++;
                            }
                            X.3Ig v11_7 = this.LC.LBL.L();
                            if (v11_7 != 0) {
                                this.ag_().LFF.L("Uploading events. Elapsed time since last upload attempt (ms)", Long.valueOf(Math.abs((v0_31 - v11_7))));
                            }
                            X.3Jq v2_135 = this.L;
                            X.3RZ.L(v2_135);
                            String v6_1 = v2_135.LCC();
                            int v4_4 = -1;
                            if (android.text.TextUtils.isEmpty(v6_1)) {
                                this.LIIJILLL = -1;
                                int v4_43 = this.L;
                                X.3RZ.L(v4_43);
                                this.L();
                                X.3Ov v0_32 = (v0_31 - X.3Pl.LD());
                                v4_43.ac_();
                                v4_43.LFFLLL();
                                try {
                                    Integer v3_82 = v4_43.LC();
                                    X.3Jq v2_206 = new String[1];
                                    v2_206[0] = String.valueOf(v0_32);
                                    Integer v3_90 = v3_82.rawQuery("select app_id from apps where app_id in (select distinct app_id from raw_events) and config_fetched_time < ? order by failed_config_fetch_time limit 1;", v2_206);
                                    try {
                                        if (v3_90.moveToFirst()) {
                                            v7_0 = v3_90.getString(0);
                                            v3_90.close();
                                            if (!android.text.TextUtils.isEmpty(v7_0)) {
                                                X.3Ov v0_19 = this.L;
                                                X.3RZ.L(v0_19);
                                                X.3Ov v0_20 = v0_19.LC(v7_0);
                                                if (v0_20 != null) {
                                                    v8 = this.LB(v0_20);
                                                }
                                            }
                                        } else {
                                            v4_43.LIIII.ag_().LFFFF.L("No expired configs for apps with pending events");
                                            v3_90.close();
                                        }
                                    } catch (X.3Jq v2_5) {
                                        v4_43.LIIII.ag_().LBL.L("Error selecting expired configs", v2_5);
                                        if (v3_90 == null) {
                                        }
                                    }
                                } catch (X.3Jq v2_5) {
                                    v3_90 = 0;
                                } catch (X.3Ov v0_17) {
                                    throw v0_17;
                                } catch (X.3Ov v0_17) {
                                    if (v3_90 == null) {
                                    } else {
                                        v3_90.close();
                                    }
                                }
                            } else {
                                if (this.LIIJILLL == -1) {
                                    String v13_0 = this.L;
                                    X.3RZ.L(v13_0);
                                    try {
                                        int v12_0 = v13_0.LC().rawQuery("select rowid from raw_events order by rowid desc limit 1;", 0);
                                        try {
                                            if (!v12_0.moveToFirst()) {
                                                v12_0.close();
                                                this.LIIJILLL = v4_4;
                                            } else {
                                                v4_4 = v12_0.getLong(0);
                                            }
                                        } catch (X.3Ig v11_2) {
                                            v13_0.LIIII.ag_().LBL.L("Error querying raw events", v11_2);
                                            if (v12_0 == 0) {
                                            } else {
                                            }
                                        }
                                    } catch (X.3Ig v11_2) {
                                        v12_0 = 0;
                                    } catch (X.3Ov v0_22) {
                                        throw v0_22;
                                    } catch (X.3Ov v0_22) {
                                        if (v12_0 == 0) {
                                        } else {
                                            v12_0.close();
                                        }
                                    }
                                }
                                int v4_5;
                                int v12_1 = this.L().LB(v6_1, X.3Oc.LCI);
                                Integer v3_5 = Math.max(0, this.L().LB(v6_1, X.3Oc.LD));
                                X.3Jq v2_15 = this.L;
                                X.3RZ.L(v2_15);
                                v2_15.ac_();
                                v2_15.LFFLLL();
                                if (v12_1 <= 0) {
                                    v4_5 = 0;
                                } else {
                                    v4_5 = 1;
                                }
                                int v4_6;
                                X.3D5.L(v4_5);
                                if (v3_5 <= null) {
                                    v4_6 = 0;
                                } else {
                                    v4_6 = 1;
                                }
                                X.3D5.L(v4_6);
                                X.3D5.L(v6_1);
                                try {
                                    X.3Oy v7_3;
                                    String v13_2 = v2_15.LC();
                                    int v4_8 = new String[1];
                                    v4_8[0] = v6_1;
                                    X.3Ir v5_4 = v13_2.query("queue", new String[] {"rowid", "data", "retry_count"}), "app_id=?", v4_8, 0, 0, "rowid", String.valueOf(v12_1));
                                    try {
                                        if (v5_4.moveToFirst()) {
                                            v7_3 = new java.util.ArrayList();
                                            X.3Ig v11_4 = 0;
                                            do {
                                                java.util.Iterator v16_1 = v5_4.getLong(v9_10);
                                                X.3Ov v9_0 = v5_4.getBlob(v10_5);
                                                X.3Iw v14_1 = v2_15.LFF.LFI;
                                                X.3RZ.L(v14_1);
                                                try {
                                                    X.3RQ v15_2 = new java.io.ByteArrayInputStream(v9_0);
                                                    String v13_4 = new java.util.zip.GZIPInputStream(v15_2);
                                                    int v12_4 = new java.io.ByteArrayOutputStream();
                                                    X.3Oy v10_0 = new byte[1024];
                                                    try {
                                                        while(true) {
                                                            X.3Ov v9_1 = v13_4.read(v10_0);
                                                            v12_4.write(v10_0, 0, v9_1);
                                                        }
                                                        v13_4.close();
                                                        v15_2.close();
                                                        String v13_5 = v12_4.toByteArray();
                                                        if ((v7_3.isEmpty()) || ((v13_5.length + v11_4) <= v3_5)) {
                                                            int v12_6 = ((X.3Iq) X.3Rb.L(X.3Ir.L(), v13_5));
                                                            if (!v5_4.isNull(2)) {
                                                                X.3Oy v10_4 = v5_4.getInt(2);
                                                                if (v12_6.LB) {
                                                                    v12_6.LIILIIL();
                                                                    v12_6.LB = 0;
                                                                }
                                                                X.3Ov v9_7 = ((X.3Ir) v12_6.L);
                                                                v9_7.zzg = (v9_7.zzg | 2);
                                                                v9_7.zzR = v10_4;
                                                            }
                                                            v11_4 += v13_5.length;
                                                            v7_3.add(android.util.Pair.create(((X.3Ir) v12_6.LIIL()), Long.valueOf(v16_1)));
                                                        } else {
                                                            break;
                                                        }
                                                    } catch (X.3Oy v10_1) {
                                                        try {
                                                            v14_1.LIIII.ag_().LBL.L("Failed to ungzip content", v10_1);
                                                            throw v10_1;
                                                        } catch (int v12_2) {
                                                            v2_15.LIIII.ag_().LBL.L("Failed to unzip queued bundle. appId", X.3Or.L(v6_1), v12_2);
                                                        }
                                                    }
                                                    if (v9_1 > null) {
                                                    }
                                                } catch (X.3Oy v10_1) {
                                                }
                                            } while((!v5_4.moveToNext()) || (v11_4 > v3_5));
                                            v5_4.close();
                                            if (!v7_3.isEmpty()) {
                                                if (this.LB(v6_1).L(X.3QC.zza)) {
                                                    int v4_36 = v7_3.iterator();
                                                    while (v4_36.hasNext()) {
                                                        Integer v3_10 = ((X.3Ir) ((android.util.Pair) v4_36.next()).first);
                                                        if (!v3_10.zzz.isEmpty()) {
                                                            X.3Ir v5_5 = v3_10.zzz;
                                                            if (v5_5 == null) {
                                                                break;
                                                            }
                                                            int v4_37 = 0;
                                                            while (v4_37 < v7_3.size()) {
                                                                Integer v3_12 = ((X.3Ir) ((android.util.Pair) v7_3.get(v4_37)).first);
                                                                if (!v3_12.zzz.isEmpty()) {
                                                                    if (!v3_12.zzz.equals(v5_5)) {
                                                                        v7_3 = v7_3.subList(0, v4_37);
                                                                        break;
                                                                    }
                                                                }
                                                                v4_37++;
                                                            }
                                                        }
                                                    }
                                                }
                                                java.util.Iterator v16_2;
                                                X.3In v17_1 = X.3Ip.L();
                                                X.3RQ v15_3 = v7_3.size();
                                                X.3Oy v10_7 = new java.util.ArrayList(v7_3.size());
                                                if (!this.L().LCC(v6_1)) {
                                                    v16_2 = 0;
                                                } else {
                                                    v16_2 = this.LB(v6_1).L(X.3QC.zza);
                                                }
                                                X.3Iw v14_2 = this.LB(v6_1).L(X.3QC.zza);
                                                String v13_6 = this.LB(v6_1).L(X.3QC.zzb);
                                                X.3MQ.LBL();
                                                int v12_8 = this.L().LC(0, X.3Oc.LILZZL);
                                                X.3Ig v11_0 = 0;
                                                while (v11_0 < v15_3) {
                                                    X.3Ov v9_15 = ((X.3Iq) ((X.3Ir) ((android.util.Pair) v7_3.get(v11_0)).first).LFFL());
                                                    v10_7.add(((Long) ((android.util.Pair) v7_3.get(v11_0)).second));
                                                    this.L();
                                                    v9_15.LIIIII();
                                                    v9_15.LFF(v0_31);
                                                    v9_15.LB(0);
                                                    if (v16_2 == null) {
                                                        v9_15.LD();
                                                    }
                                                    if (v14_2 == null) {
                                                        if (v9_15.LB) {
                                                            v9_15.LIILIIL();
                                                            v9_15.LB = 0;
                                                        }
                                                        int v4_49 = ((X.3Ir) v9_15.L);
                                                        v4_49.zzf = (v4_49.zzf & -65537);
                                                        v4_49.zzz = X.3Ir.zze.zzz;
                                                        if (v9_15.LB) {
                                                            v9_15.LIILIIL();
                                                            v9_15.LB = 0;
                                                        }
                                                        int v4_51 = ((X.3Ir) v9_15.L);
                                                        v4_51.zzf = (v4_51.zzf & -131073);
                                                        v4_51.zzA = 0;
                                                    }
                                                    if (v13_6 == null) {
                                                        v9_15.LCC();
                                                    }
                                                    this.L(v6_1, v9_15);
                                                    if (v12_8 == 0) {
                                                        v9_15.LI();
                                                    }
                                                    if (this.L().LC(v6_1, X.3Oc.LIIZ)) {
                                                        Integer v3_0 = ((X.3Ir) v9_15.LIIL()).LF();
                                                        X.3Jq v2_2 = this.LFI;
                                                        X.3RZ.L(v2_2);
                                                        X.3Jq v2_3 = v2_2.L(v3_0);
                                                        if (v9_15.LB) {
                                                            v9_15.LIILIIL();
                                                            v9_15.LB = 0;
                                                        }
                                                        X.3Ir v5_1 = ((X.3Ir) v9_15.L);
                                                        v5_1.zzg = (v5_1.zzg | 32);
                                                        v5_1.zzW = v2_3;
                                                    }
                                                    v17_1.L(v9_15);
                                                    v11_0++;
                                                }
                                                X.3Ov v9_11;
                                                if (!android.util.Log.isLoggable(this.ag_().LB(), 2)) {
                                                    v9_11 = 0;
                                                } else {
                                                    X.3Ov v9_12 = this.LFI;
                                                    X.3RZ.L(v9_12);
                                                    Integer v3_19 = ((X.3Ip) v17_1.LIIL());
                                                    if (v3_19 != null) {
                                                        X.3Oy v7_5 = new StringBuilder();
                                                        v7_5.append("\nbatch {\n");
                                                        java.util.Iterator v19_1 = v3_19.zze.iterator();
                                                        while (v19_1.hasNext()) {
                                                            X.3Ig v11_6 = ((X.3Ir) v19_1.next());
                                                            if (v11_6 != null) {
                                                                X.3Rb.L(v7_5, 1);
                                                                v7_5.append("bundle {\n");
                                                                if ((v11_6.zzf & 1) != 0) {
                                                                    X.3Rb.L(v7_5, 1, "protocol_version", Integer.valueOf(v11_6.zzh));
                                                                }
                                                                X.3MQ.LBL();
                                                                if ((v9_12.LIIII.LCCII.LC(0, X.3Oc.LILZZL)) && ((v11_6.zzg & 8192) != 0)) {
                                                                    X.3Rb.L(v7_5, 1, "session_stitching_token", v11_6.zzae);
                                                                }
                                                                X.3Rb.L(v7_5, 1, "platform", v11_6.zzp);
                                                                if ((v11_6.zzf & 16384) != 0) {
                                                                    X.3Rb.L(v7_5, 1, "gmp_version", Long.valueOf(v11_6.zzx));
                                                                }
                                                                if ((v11_6.zzf & 32768) != 0) {
                                                                    X.3Rb.L(v7_5, 1, "uploading_gmp_version", Long.valueOf(v11_6.zzy));
                                                                }
                                                                if ((v11_6.zzg & 16) != 0) {
                                                                    X.3Rb.L(v7_5, 1, "dynamite_version", Long.valueOf(v11_6.zzV));
                                                                }
                                                                if ((v11_6.zzf & 536870912) != 0) {
                                                                    X.3Rb.L(v7_5, 1, "config_version", Long.valueOf(v11_6.zzN));
                                                                }
                                                                X.3Rb.L(v7_5, 1, "gmp_app_id", v11_6.zzF);
                                                                X.3Rb.L(v7_5, 1, "admob_app_id", v11_6.zzS);
                                                                X.3Rb.L(v7_5, 1, "app_id", v11_6.zzv);
                                                                X.3Rb.L(v7_5, 1, "app_version", v11_6.zzw);
                                                                if ((v11_6.zzf & 33554432) != 0) {
                                                                    X.3Rb.L(v7_5, 1, "app_version_major", Integer.valueOf(v11_6.zzJ));
                                                                }
                                                                X.3Rb.L(v7_5, 1, "firebase_instance_id", v11_6.zzI);
                                                                if ((v11_6.zzf & 524288) != 0) {
                                                                    X.3Rb.L(v7_5, 1, "dev_cert_hash", Long.valueOf(v11_6.zzC));
                                                                }
                                                                X.3Rb.L(v7_5, 1, "app_store", v11_6.zzu);
                                                                if ((v11_6.zzf & 2) != 0) {
                                                                    X.3Rb.L(v7_5, 1, "upload_timestamp_millis", Long.valueOf(v11_6.zzk));
                                                                }
                                                                if ((v11_6.zzf & 4) != 0) {
                                                                    X.3Rb.L(v7_5, 1, "start_timestamp_millis", Long.valueOf(v11_6.zzl));
                                                                }
                                                                if (v11_6.LC()) {
                                                                    X.3Rb.L(v7_5, 1, "end_timestamp_millis", Long.valueOf(v11_6.zzm));
                                                                }
                                                                if ((v11_6.zzf & 16) != 0) {
                                                                    X.3Rb.L(v7_5, 1, "previous_bundle_start_timestamp_millis", Long.valueOf(v11_6.zzn));
                                                                }
                                                                if ((v11_6.zzf & 32) != 0) {
                                                                    X.3Rb.L(v7_5, 1, "previous_bundle_end_timestamp_millis", Long.valueOf(v11_6.zzo));
                                                                }
                                                                X.3Rb.L(v7_5, 1, "app_instance_id", v11_6.zzB);
                                                                X.3Rb.L(v7_5, 1, "resettable_device_id", v11_6.zzz);
                                                                X.3Rb.L(v7_5, 1, "ds_id", v11_6.zzP);
                                                                if ((v11_6.zzf & 131072) != 0) {
                                                                    X.3Rb.L(v7_5, 1, "limited_ad_tracking", Boolean.valueOf(v11_6.zzA));
                                                                }
                                                                X.3Rb.L(v7_5, 1, "os_version", v11_6.zzq);
                                                                X.3Rb.L(v7_5, 1, "device_model", v11_6.zzr);
                                                                X.3Rb.L(v7_5, 1, "user_default_language", v11_6.zzs);
                                                                if ((v11_6.zzf & 1024) != 0) {
                                                                    X.3Rb.L(v7_5, 1, "time_zone_offset_minutes", Integer.valueOf(v11_6.zzt));
                                                                }
                                                                if ((v11_6.zzf & 1048576) != 0) {
                                                                    X.3Rb.L(v7_5, 1, "bundle_sequential_index", Integer.valueOf(v11_6.zzD));
                                                                }
                                                                if ((v11_6.zzf & 8388608) != 0) {
                                                                    X.3Rb.L(v7_5, 1, "service_upload", Boolean.valueOf(v11_6.zzG));
                                                                }
                                                                X.3Rb.L(v7_5, 1, "health_monitor", v11_6.zzE);
                                                                if (v11_6.LCC()) {
                                                                    X.3Rb.L(v7_5, 1, "retry_counter", Integer.valueOf(v11_6.zzR));
                                                                }
                                                                if ((v11_6.zzg & 128) != 0) {
                                                                    X.3Rb.L(v7_5, 1, "consent_signals", v11_6.zzY);
                                                                }
                                                                X.3Jq v2_141 = v11_6.zzj;
                                                                if (v2_141 != null) {
                                                                    java.util.Iterator v16_3 = v2_141.iterator();
                                                                    while (v16_3.hasNext()) {
                                                                        X.3Iw v14_8 = ((X.3J0) v16_3.next());
                                                                        if (v14_8 != null) {
                                                                            Integer v3_75;
                                                                            X.3Rb.L(v7_5, 2);
                                                                            v7_5.append("user_property {\n");
                                                                            if (!v14_8.LC()) {
                                                                                v3_75 = 0;
                                                                            } else {
                                                                                v3_75 = Long.valueOf(v14_8.zzf);
                                                                            }
                                                                            Integer v3_78;
                                                                            X.3Rb.L(v7_5, 2, "set_timestamp_millis", v3_75);
                                                                            X.3Rb.L(v7_5, 2, "name", v9_12.LIIII.LF.LBL(v14_8.zzg));
                                                                            X.3Rb.L(v7_5, 2, "string_value", v14_8.zzh);
                                                                            if (!v14_8.LBL()) {
                                                                                v3_78 = 0;
                                                                            } else {
                                                                                v3_78 = Long.valueOf(v14_8.zzi);
                                                                            }
                                                                            Integer v3_79;
                                                                            X.3Rb.L(v7_5, 2, "int_value", v3_78);
                                                                            if (!v14_8.LB()) {
                                                                                v3_79 = 0;
                                                                            } else {
                                                                                v3_79 = Double.valueOf(v14_8.zzk);
                                                                            }
                                                                            X.3Rb.L(v7_5, 2, "double_value", v3_79);
                                                                            X.3Rb.L(v7_5, 2);
                                                                            v7_5.append("}\n");
                                                                        }
                                                                    }
                                                                }
                                                                X.3Jq v2_143 = v11_6.zzH;
                                                                if (v2_143 != null) {
                                                                    java.util.Iterator v16_4 = v2_143.iterator();
                                                                    while (v16_4.hasNext()) {
                                                                        Integer v3_73 = ((X.3Ib) v16_4.next());
                                                                        if (v3_73 != null) {
                                                                            X.3Rb.L(v7_5, 2);
                                                                            v7_5.append("audience_membership {\n");
                                                                            if ((v3_73.zze & 1) != 0) {
                                                                                X.3Rb.L(v7_5, 2, "audience_id", Integer.valueOf(v3_73.zzf));
                                                                            }
                                                                            if ((v3_73.zze & 8) != 0) {
                                                                                X.3Rb.L(v7_5, 2, "new_audience", Boolean.valueOf(v3_73.zzi));
                                                                            }
                                                                            X.3Rb.L(v7_5, "current_data", v3_73.LB());
                                                                            if ((v3_73.zze & 4) != 0) {
                                                                                Integer v3_74 = v3_73.zzh;
                                                                                if (v3_74 == null) {
                                                                                    v3_74 = X.3Iw.zza;
                                                                                }
                                                                                X.3Rb.L(v7_5, "previous_data", v3_74);
                                                                            }
                                                                            X.3Rb.L(v7_5, 2);
                                                                            v7_5.append("}\n");
                                                                        }
                                                                    }
                                                                }
                                                                X.3Jq v2_145 = v11_6.zzi;
                                                                if (v2_145 != null) {
                                                                    X.3Iw v14_3 = v2_145.iterator();
                                                                    while (v14_3.hasNext()) {
                                                                        X.3Ig v11_9 = ((X.3Ig) v14_3.next());
                                                                        if (v11_9 != null) {
                                                                            X.3Rb.L(v7_5, 2);
                                                                            v7_5.append("event {\n");
                                                                            X.3Rb.L(v7_5, 2, "name", v9_12.LIIII.LF.L(v11_9.zzg));
                                                                            if (v11_9.LC()) {
                                                                                X.3Rb.L(v7_5, 2, "timestamp_millis", Long.valueOf(v11_9.zzh));
                                                                            }
                                                                            if ((v11_9.zze & 4) != 0) {
                                                                                X.3Rb.L(v7_5, 2, "previous_timestamp_millis", Long.valueOf(v11_9.zzi));
                                                                            }
                                                                            if ((v11_9.zze & 8) != 0) {
                                                                                X.3Rb.L(v7_5, 2, "count", Integer.valueOf(v11_9.zzj));
                                                                            }
                                                                            if (v11_9.L() != 0) {
                                                                                X.3Rb.L(v9_12, v7_5, 2, v11_9.zzf);
                                                                            }
                                                                            X.3Rb.L(v7_5, 2);
                                                                            v7_5.append("}\n");
                                                                        }
                                                                    }
                                                                }
                                                                X.3Rb.L(v7_5, 1);
                                                                v7_5.append("}\n");
                                                            }
                                                        }
                                                        v7_5.append("}\n");
                                                        v9_11 = v7_5.toString();
                                                    } else {
                                                        v9_11 = "";
                                                    }
                                                }
                                                Integer v3_84;
                                                X.3RZ.L(this.LFI);
                                                X.3Ir v5_8 = ((X.3Ip) v17_1.LIIL()).LF();
                                                int v4_44 = this.LFLL;
                                                X.3MK.LBL();
                                                if (!v4_44.LIIII.LCCII.LC(v6_1, X.3Oc.LILZ)) {
                                                    v3_84 = ((String) X.3Oc.LICI.L(0));
                                                } else {
                                                    X.3Jq v2_201 = v4_44.LFF.LFF;
                                                    X.3RZ.L(v2_201);
                                                    v2_201.ac_();
                                                    X.3PI.LFI(v2_201, v6_1);
                                                    X.3Ig v11_11 = ((String) v2_201.LFFL.get(v6_1));
                                                    if (android.text.TextUtils.isEmpty(v11_11)) {
                                                        v3_84 = ((String) X.3Oc.LICI.L(0));
                                                    } else {
                                                        X.3Jq v2_210 = android.net.Uri.parse(((String) X.3Oc.LICI.L(0)));
                                                        X.3Oy v7_6 = v2_210.buildUpon();
                                                        int v4_45 = v2_210.getAuthority();
                                                        Integer v3_89 = new StringBuilder();
                                                        v3_89.append(v11_11);
                                                        v3_89.append(".");
                                                        v3_89.append(v4_45);
                                                        v7_6.authority(v3_89.toString());
                                                        v3_84 = v7_6.build().toString();
                                                    }
                                                }
                                                int v4_47 = new java.net.URL(v3_84);
                                                X.3D5.L((v10_7.isEmpty() ^ 1));
                                                if (this.LIIIL == null) {
                                                    this.LIIIL = new java.util.ArrayList(v10_7);
                                                } else {
                                                    this.ag_().LBL.L("Set uploading progress before finishing the previous upload");
                                                }
                                                this.LC.LC.L(v0_31);
                                                X.3Oy v10_9 = "?";
                                                if (v15_3 > null) {
                                                    v10_9 = ((X.3Ir) ((X.3Ip) v17_1.L).zze.get(0)).zzv;
                                                }
                                                this.ag_().LFFFF.L("Uploading data. app, uncompressed size, data", v10_9, Integer.valueOf(v5_8.length), v9_11);
                                                this.LIIIII = 1;
                                                X.3Oy v7_8 = this.LFFFF;
                                                X.3RZ.L(v7_8);
                                                X.3Jq v2_225 = new X.3RQ(this);
                                                v7_8.ac_();
                                                v7_8.LFFLLL();
                                                X.3D5.L(v4_47);
                                                X.3D5.L(v5_8);
                                                X.3D5.L(v2_225);
                                                X.3PP v1_11 = v7_8.LIIII.ah_();
                                                X.3Ov v0_46 = new X.3Ov;
                                                v0_46(v7_8, v6_1, v4_47, v5_8, 0, v2_225);
                                                v1_11.L(v0_46);
                                            }
                                        } else {
                                            v7_3 = java.util.Collections.emptyList();
                                            v5_4.close();
                                        }
                                    } catch (X.3Oy v7_1) {
                                        v2_15.LIIII.ag_().LBL.L("Error querying bundles. appId", X.3Or.L(v6_1), v7_1);
                                        v7_3 = java.util.Collections.emptyList();
                                        if (v5_4 == null) {
                                        } else {
                                            v5_4.close();
                                        }
                                    }
                                } catch (X.3Oy v7_1) {
                                    v5_4 = 0;
                                } catch (X.3Ov v0_25) {
                                    throw v0_25;
                                } catch (X.3Ov v0_25) {
                                    if (v5_4 == null) {
                                    } else {
                                        v5_4.close();
                                    }
                                }
                            }
                            v8.LIIIIZ = 0;
                        } else {
                            this.ag_().LFFFF.L("Network not connected, ignoring upload request");
                            this.LFI();
                            this.LIIIIZ = 0;
                        }
                    } else {
                        this.ag_().LFFFF.L("Uploading requested multiple times");
                        this.LIIIIZ = 0;
                    }
                } else {
                    this.LFI();
                    this.LIIIIZ = 0;
                }
            } else {
                this.ag_().LBL.L("Upload called in the client side when service should be used");
                this.LIIIIZ = 0;
            }
        } else {
            this.ag_().LCCII.L("Upload data called on the client side before use of service was decided");
            this.LIIIIZ = 0;
        }
        v8.LII();
        return;
    }


}