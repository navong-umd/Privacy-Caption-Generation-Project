/*Application Package Name: com.tiktok.lite.go
class PRCS_393 {
/**
X.3Rv;L(Landroid/accounts/AccountManager; Ljava/lang/String; [Ljava/lang/String; Ljava/lang/String;)Landroid/accounts/AccountManagerFuture;
*/

    public static android.accounts.AccountManagerFuture L(android.accounts.AccountManager p17, String p18, String[] p19, String p20)
    {
        com.bytedance.helios.statichook.api.HeliosApiHook v5_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
        Object[] v11 = new Object[4];
        v11[0] = p18;
        v11[1] = p19;
        v11[2] = 0;
        v11[3] = 0;
        com.bytedance.helios.statichook.api.ExtraInfo v12_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "(Ljava/lang/String;[Ljava/lang/String;Landroid/accounts/AccountManagerCallback;Landroid/os/Handler;)Landroid/accounts/AccountManagerFuture;", p20);
        com.bytedance.helios.statichook.api.Result v1_0 = v5_1.preInvoke(102502, "android/accounts/AccountManager", "getAccountsByTypeAndFeatures", p17, v11, "android.accounts.AccountManagerFuture", v12_1);
        if (!v1_0.intercept) {
            android.accounts.AccountManagerFuture v6_1 = p17.getAccountsByTypeAndFeatures(p18, p19, 0, 0);
            v5_1.postInvoke(v6_1, 102502, "android/accounts/AccountManager", "getAccountsByTypeAndFeatures", p17, v11, v12_1, 1);
            return v6_1;
        } else {
            v5_1.postInvoke(0, 102502, "android/accounts/AccountManager", "getAccountsByTypeAndFeatures", p17, v11, v12_1, 0);
            return ((android.accounts.AccountManagerFuture) v1_0.returnValue);
        }
    }

/**
X.3Rv;LBL()Z
*/

    public final boolean LBL()
    {
        this.ac_();
        Boolean v1_4 = this.LIIII.LFF.L();
        if ((v1_4 - this.LB) > 86400000) {
            this.L = 0;
        }
        Boolean v3_11 = this.L;
        if (v3_11 != null) {
            return v3_11.booleanValue();
        } else {
            android.accounts.AccountManager v5_3;
            android.content.Context v7 = this.LIIII.L;
            com.bytedance.helios.statichook.api.HeliosApiHook v11_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
            X.3Oo v4_2 = new Object[2];
            v4_2[0] = v7;
            v4_2[1] = "android.permission.GET_ACCOUNTS";
            com.bytedance.helios.statichook.api.ExtraInfo v9_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "(Landroid/content/Context;Ljava/lang/String;)I", "dzBzEgU1UM3QUBkgSxaWaaw9Bz14/yzxe1dYm0ZJPLqwOID9zPVdd3eEmUDB28GN");
            com.bytedance.helios.statichook.api.HeliosApiHook v11_2 = v11_1;
            android.accounts.AccountManager v5_2 = v11_2.preInvoke(2908, "androidx/core/content/ContextCompat", "checkSelfPermission", X.04U, v4_2, "int", v9_1);
            if (!v5_2.intercept) {
                v5_3 = X.04U.L(v7, "android.permission.GET_ACCOUNTS");
                v11_2.postInvoke(Integer.valueOf(v5_3), 2908, "androidx/core/content/ContextCompat", "checkSelfPermission", X.04U, v4_2, v9_1, 1);
            } else {
                v11_2.postInvoke(0, 2908, "androidx/core/content/ContextCompat", "checkSelfPermission", X.04U, v4_2, v9_1, 0);
                v5_3 = ((Integer) v5_2.returnValue).intValue();
            }
            if (v5_3 == null) {
                if (this.LCC == null) {
                    this.LCC = android.accounts.AccountManager.get(this.LIIII.L);
                }
                try {
                    X.3Oo v4_13 = ((android.accounts.Account[]) X.3Rv.L(this.LCC, "com.google", new String[] {"service_HOSTED"}), "dzBzEgU1UM3QUBkgSxaWaaw9Bz14/yzxe1dYm0ZJPLqwOID9zPVdd3eEmUDB28GN").getResult());
                } catch (android.accounts.AccountManager v5_0) {
                    this.LIIII.ag_().LC.L("Exception checking account types", v5_0);
                    this.LB = v1_4;
                    this.L = Boolean.valueOf(0);
                    return 0;
                } catch (android.accounts.AccountManager v5_0) {
                } catch (android.accounts.AccountManager v5_0) {
                }
                if ((v4_13 == null) || (v4_13.length <= 0)) {
                    Boolean v3_18 = ((android.accounts.Account[]) X.3Rv.L(this.LCC, "com.google", new String[] {"service_uca"}), "dzBzEgU1UM3QUBkgSxaWaaw9Bz14/yzxe1dYm0ZJPLqwOID9zPVdd3eEmUDB28GN").getResult());
                    if ((v3_18 == null) || (v3_18.length <= 0)) {
                        this.LB = v1_4;
                        this.L = Boolean.valueOf(0);
                        return 0;
                    } else {
                        this.L = Boolean.valueOf(1);
                        this.LB = v1_4;
                        return 1;
                    }
                } else {
                    this.L = Boolean.valueOf(1);
                    this.LB = v1_4;
                    return 1;
                }
            } else {
                this.LIIII.ag_().LCI.L("Permission error checking for dasher/unicorn accounts");
                this.LB = v1_4;
                this.L = Boolean.valueOf(0);
                return 0;
            }
        }
    }

/**
X.3Pf;call()Ljava/lang/Object;
*/

    public final synthetic Object call()
    {
        this.LBL.L.LFFL();
        String v0_0 = this.LBL.L.LBL;
        X.3RZ.L(v0_0);
        X.3Oo v2_44 = this.L;
        long v7_0 = this.LB;
        v0_0.ac_();
        X.3PS.LIIIIZZ();
        X.3D5.L(v2_44);
        X.3D5.L(v7_0);
        if (v0_0.LIIII.LCCII.LC(v7_0, X.3Oc.LIILZZLLZL)) {
            if (("_iap".equals(v2_44.L)) || ("_iapx".equals(v2_44.L))) {
                X.3In v14 = X.3Ip.L();
                Object v1_15 = v0_0.LFF.L;
                X.3RZ.L(v1_15);
                v1_15.LCCII();
                try {
                    byte[] v4_1;
                    Object v1_17 = v0_0.LFF.L;
                    X.3RZ.L(v1_17);
                    X.3Pm v11 = v1_17.LC(v7_0);
                } catch (Object v1_34) {
                    String v0_9 = v0_0.LFF.L;
                    X.3RZ.L(v0_9);
                    v0_9.LCI();
                    throw v1_34;
                }
                if (v11 != null) {
                    if (v11.LIIIJJLL()) {
                        Object v1_19 = X.3Ir.L();
                        v1_19.LIIII();
                        v1_19.LIII();
                        if (!android.text.TextUtils.isEmpty(v11.LFFLLL())) {
                            v1_19.LB(v11.LFFLLL());
                        }
                        if (!android.text.TextUtils.isEmpty(v11.LFLL())) {
                            X.3Nc v6_25 = v11.LFLL();
                            java.util.Objects.requireNonNull(v6_25, "null reference");
                            v1_19.LC(v6_25);
                        }
                        if (!android.text.TextUtils.isEmpty(v11.LI())) {
                            X.3Nc v6_30 = v11.LI();
                            java.util.Objects.requireNonNull(v6_30, "null reference");
                            v1_19.LCC(v6_30);
                        }
                        if (v11.LB() != -2147483648) {
                            v1_19.LC(((int) v11.LB()));
                        }
                        v1_19.LCCII(v11.LCI());
                        v1_19.LC(v11.LCC());
                        long v8_11 = v11.LII();
                        X.3Nc v6_31 = v11.LFFL();
                        if (android.text.TextUtils.isEmpty(v8_11)) {
                            if (!android.text.TextUtils.isEmpty(v6_31)) {
                                v1_19.L(v6_31);
                            }
                        } else {
                            v1_19.LFF(v8_11);
                        }
                        long v8_0 = v0_0.LFF.LB(v7_0);
                        v1_19.LBL(v11.LC());
                        if ((v0_0.LIIII.LIIII()) && ((v0_0.LIIII.LCCII.LCC(v1_19.LIIIIZ())) && ((v8_0.L(X.3QC.zza)) && (!android.text.TextUtils.isEmpty(0))))) {
                            v1_19.LII();
                        }
                        v1_19.LCCII(v8_0.LBL());
                        if ((v8_0.L(X.3QC.zza)) && ((!v0_0.LIIII.LCCII.LC(0, X.3Oc.LILLII)) || (v11.LIIIIZZ()))) {
                            X.3Nc v6_3 = v0_0.LFF.LC.L(v11.LFFLLL(), v8_0);
                            if (v11.LIIIIZZ()) {
                                if (!android.text.TextUtils.isEmpty(((CharSequence) v6_3.first))) {
                                    v1_19.LFFLLL(X.3QR.LCC());
                                    if (v6_3.second != null) {
                                        v1_19.L(((Boolean) v6_3.second).booleanValue());
                                    }
                                }
                            }
                        }
                        v0_0.LIIII.LCC().LCI();
                        v1_19.LCI(android.os.Build.MODEL);
                        v0_0.LIIII.LCC().LCI();
                        v1_19.LFFL(android.os.Build$VERSION.RELEASE);
                        int v5_38 = v0_0.LIIII.LCC();
                        v5_38.LCI();
                        v1_19.LCI(((int) v5_38.LBL));
                        int v5_41 = v0_0.LIIII.LCC();
                        v5_41.LCI();
                        v1_19.LFLL(v5_41.LC);
                        try {
                            if ((v8_0.L(X.3QC.zzb)) && (v11.LFI() != null)) {
                                X.3D5.L(v11.LFI());
                                v1_19.LBL(X.3QR.LCC());
                            }
                        } catch (int v5_48) {
                            v0_0.LIIII.ag_().LFF.L("app instance id encryption failed", v5_48.getMessage());
                            v4_1 = new byte[0];
                            v0_0 = v0_0.LFF;
                        }
                        if (!android.text.TextUtils.isEmpty(v11.LICI())) {
                            int v5_50 = v11.LICI();
                            java.util.Objects.requireNonNull(v5_50, "null reference");
                            v1_19.LF(v5_50);
                        }
                        java.io.IOException v3_5 = v11.LFFLLL();
                        int v5_52 = v0_0.LFF.L;
                        X.3RZ.L(v5_52);
                        int v5_53 = v5_52.LCC(v3_5);
                        String v12_0 = v5_53.iterator();
                        while (v12_0.hasNext()) {
                            X.3Ii v10_1 = ((X.3Rd) v12_0.next());
                            if ("_lte".equals(v10_1.LBL)) {
                            }
                            if ((v10_1 == null) || (v10_1.LCC == null)) {
                                byte[] v4_5 = new X.3Rd;
                                v4_5(v3_5, "auto", "_lte", v0_0.LIIII.LFF.L(), Long.valueOf(0));
                                v5_53.add(v4_5);
                                java.io.IOException v3_7 = v0_0.LFF.L;
                                X.3RZ.L(v3_7);
                                v3_7.L(v4_5);
                            }
                            X.3Nc v6_9 = v0_0.LFF.LFI;
                            X.3RZ.L(v6_9);
                            v6_9.LIIII.ag_().LFFFF.L("Checking account type status for ad personalization signals");
                            if (v6_9.LIIII.LCC().LBL()) {
                                byte[] v4_7 = v11.LFFLLL();
                                X.3D5.L(v4_7);
                                if (v11.LIIIIZZ()) {
                                    java.io.IOException v3_17 = v6_9.LFF.LFF;
                                    X.3RZ.L(v3_17);
                                    if (v3_17.LC(v4_7)) {
                                        v6_9.LIIII.ag_().LFF.L("Turning off ad personalization due to account type");
                                        X.3Ii v10_3 = v5_53.iterator();
                                        while (v10_3.hasNext()) {
                                            if ("_npa".equals(((X.3Rd) v10_3.next()).LBL)) {
                                                v10_3.remove();
                                                break;
                                            }
                                        }
                                        java.io.IOException v3_27 = new X.3Rd;
                                        v3_27(v4_7, "auto", "_npa", v6_9.LIIII.LFF.L(), Long.valueOf(1));
                                        v5_53.add(v3_27);
                                    }
                                }
                            }
                            long v8_4 = new X.3J0[v5_53.size()];
                            X.3Nc v6_12 = 0;
                            while (v6_12 < v5_53.size()) {
                                X.3Ii v10_6 = X.3J0.L();
                                v10_6.L(((X.3Rd) v5_53.get(v6_12)).LBL);
                                v10_6.LB(((X.3Rd) v5_53.get(v6_12)).LC);
                                byte[] v4_18 = v0_0.LFF.LFI;
                                X.3RZ.L(v4_18);
                                v4_18.L(v10_6, ((X.3Rd) v5_53.get(v6_12)).LCC);
                                v8_4[v6_12] = ((X.3J0) v10_6.LIIL());
                                v6_12++;
                            }
                            byte[] v4_8 = java.util.Arrays.asList(v8_4);
                            if (v1_19.LB) {
                                v1_19.LIILIIL();
                                v1_19.LB = 0;
                            }
                            java.io.IOException v3_33 = ((X.3Ir) v1_19.L);
                            v3_33.LBL();
                            X.3I3.L(v4_8, v3_33.zzj);
                            int v5_55 = X.3Os.L(v2_44);
                            X.3Nc v6_13 = v0_0.LIIII.LFLL();
                            byte[] v4_9 = v5_55.LB;
                            java.io.IOException v3_37 = v0_0.LFF.L;
                            X.3RZ.L(v3_37);
                            v6_13.L(v4_9, v3_37.LBL(v7_0));
                            v0_0.LIIII.LFLL().L(v5_55, v0_0.LIIII.LCCII.LB(v7_0));
                            long v8_5 = v5_55.LB;
                            v8_5.putLong("_c", 1);
                            v0_0.LIIII.ag_().LFF.L("Marking in-app purchase as real-time");
                            v8_5.putLong("_r", 1);
                            v8_5.putString("_o", v2_44.LBL);
                            if (v0_0.LIIII.LFLL().LC(v1_19.LIIIIZ())) {
                                int v5_57 = v0_0.LIIII.LFLL();
                                byte[] v4_14 = Long.valueOf(1);
                                v5_57.L(v8_5, "_dbg", v4_14);
                                v0_0.LIIII.LFLL().L(v8_5, "_r", v4_14);
                            }
                            String v32;
                            X.3Rx v15_0;
                            byte[] v4_16;
                            int v9_1;
                            byte[] v4_15 = v0_0.LFF.L;
                            X.3RZ.L(v4_15);
                            java.io.IOException v3_59 = v4_15.LBL(v7_0, v2_44.L);
                            if (v3_59 != null) {
                                v32 = v7_0;
                                v4_16 = 0;
                                v9_1 = v3_59.LCCII;
                                v15_0 = v3_59.L(v2_44.LC);
                            } else {
                                v9_1 = 0;
                                v32 = v7_0;
                                v4_16 = 0;
                                v15_0 = new X.3Rx(v7_0, v2_44.L, 0, 0, 0, v2_44.LC, 0, 0, 0, 0, 0);
                            }
                            java.io.IOException v3_62 = v0_0.LFF.L;
                            X.3RZ.L(v3_62);
                            v3_62.L(v15_0);
                            java.io.IOException v3_63 = new X.3Rw;
                            v3_63(v0_0.LIIII, v2_44.LBL, v32, v2_44.L, v2_44.LC, v9_1, v8_5);
                            int v5_61 = X.3Ig.LB();
                            v5_61.LB(v3_63.LBL);
                            v5_61.L(v3_63.LB);
                            v5_61.L(v3_63.LC);
                            int v9_3 = new X.3Ry(v3_63.LCC);
                            while (v9_3.hasNext()) {
                                long v7_6 = v9_3.L();
                                long v8_9 = X.3Ik.LB();
                                v8_9.L(v7_6);
                                long v7_7 = v3_63.LCC.L.get(v7_6);
                                if (v7_7 != 0) {
                                    X.3Nc v6_29 = v0_0.LFF.LFI;
                                    X.3RZ.L(v6_29);
                                    v6_29.L(v8_9, v7_7);
                                    v5_61.L(v8_9);
                                }
                            }
                            v1_19.L(v5_61);
                            long v8_7 = ((X.3Is) X.3Iu.zza.LFFFF());
                            java.io.IOException v3_67 = ((X.3Ih) X.3Ii.zza.LFFFF());
                            X.3Nc v6_19 = v15_0.LBL;
                            if (v3_67.LB) {
                                v3_67.LIILIIL();
                                v3_67.LB = 0;
                            }
                            X.3Ii v10_5 = ((X.3Ii) v3_67.L);
                            v10_5.zze = (v10_5.zze | 2);
                            v10_5.zzg = v6_19;
                            long v7_2 = v2_44.L;
                            if (v3_67.LB) {
                                v3_67.LIILIIL();
                                v3_67.LB = 0;
                            }
                            X.3Nc v6_21 = ((X.3Ii) v3_67.L);
                            v6_21.zze = (v6_21.zze | 1);
                            v6_21.zzf = v7_2;
                            if (v8_7.LB) {
                                v8_7.LIILIIL();
                                v8_7.LB = 0;
                            }
                            long v7_4 = ((X.3Iu) v8_7.L);
                            X.3Nc v6_23 = ((X.3Ii) v3_67.LIIL());
                            java.io.IOException v3_68 = v7_4.zzg;
                            if (!v3_68.LBL()) {
                                v7_4.zzg = X.3I4.L(v3_68);
                            }
                            v7_4.zzg.add(v6_23);
                            if (v1_19.LB) {
                                v1_19.LIILIIL();
                                v1_19.LB = 0;
                            }
                            java.io.IOException v3_70 = ((X.3Ir) v1_19.L);
                            v3_70.zzT = ((X.3Iu) v8_7.LIIL());
                            v3_70.zzg = (v3_70.zzg | 8);
                            X.3Nc v6_24 = v0_0.LFF.LB;
                            X.3RZ.L(v6_24);
                            v1_19.L(v6_24.L(v11.LFFLLL(), java.util.Collections.emptyList(), v1_19.LIIILL(), Long.valueOf(v5_61.LBL()), Long.valueOf(v5_61.LBL())));
                            if (((X.3Ig) v5_61.L).LC()) {
                                v1_19.LF(v5_61.LBL());
                                v1_19.LCC(v5_61.LBL());
                            }
                            X.3Oo v2_26 = v11.LD();
                            long v8_8 = v2_26 cmp 0;
                            if (v8_8 != 0) {
                                v1_19.LCI(v2_26);
                            }
                            int v5_65 = v11.LFF();
                            if (v5_65 == 0) {
                                if (v8_8 != 0) {
                                    v1_19.LD(v2_26);
                                }
                            } else {
                                v1_19.LD(v5_65);
                            }
                            int v5_66 = v11.LIIII();
                            X.3MQ.LBL();
                            if (v0_0.LIIII.LCCII.LC(v4_16, X.3Oc.LILZZL)) {
                                if (v5_66 != 0) {
                                    v1_19.LFI(v5_66);
                                }
                            }
                            v11.LIIIIZ();
                            v1_19.LCC(((int) v11.LF()));
                            v1_19.LIIIII();
                            v1_19.LFF(v0_0.LIIII.LFF.L());
                            v1_19.LB(1);
                            if (v0_0.LIIII.LCCII.LC(v4_16, X.3Oc.LJIII)) {
                                v0_0.LFF.L(v1_19.LIIIIZ(), v1_19);
                            }
                            v14.L(v1_19);
                            v11.LF(v1_19.LC());
                            v11.LCI(v1_19.LBL());
                            Object v1_22 = v0_0.LFF.L;
                            X.3RZ.L(v1_22);
                            v1_22.L(v11);
                            Object v1_24 = v0_0.LFF.L;
                            X.3RZ.L(v1_24);
                            v1_24.LF();
                            Object v1_26 = v0_0.LFF.L;
                            X.3RZ.L(v1_26);
                            v1_26.LCI();
                            try {
                                X.3Oo v2_40 = v0_0.LFF.LFI;
                                X.3RZ.L(v2_40);
                                byte[] v4_17 = v2_40.LB(v14.LIIL().LF());
                                return v4_17;
                            } catch (java.io.IOException v3_74) {
                                v0_0.LIIII.ag_().LBL.L("Data loss. Failed to bundle and serialize. appId", X.3Or.L(v32), v3_74);
                                return v4_17;
                            }
                        }
                        v10_1 = 0;
                    } else {
                        v0_0.LIIII.ag_().LFF.L("Log and bundle disabled. package_name", v7_0);
                        v4_1 = new byte[0];
                        v0_0 = v0_0.LFF;
                    }
                } else {
                    v0_0.LIIII.ag_().LFF.L("Log and bundle not available. package_name", v7_0);
                    v4_1 = new byte[0];
                    v0_0 = v0_0.LFF;
                }
                String v0_10 = v0_0.L;
                X.3RZ.L(v0_10);
                v0_10.LCI();
                return v4_1;
            } else {
                v0_0.LIIII.ag_().LFF.L("Generating a payload for this event is not available. package_name, event_name", v7_0, v2_44.L);
                return 0;
            }
        } else {
            v0_0.LIIII.ag_().LFF.L("Generating ScionPayload disabled. packageName", v7_0);
            byte[] v4_19 = new byte[0];
            return v4_19;
        }
    }


}