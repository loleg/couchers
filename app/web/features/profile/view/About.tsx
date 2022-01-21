import { Typography } from "@material-ui/core";
import Divider from "components/Divider";
import Markdown from "components/Markdown";
import { NONE } from "features/constants";
import { useTranslation } from "i18n";
import { GLOBAL,PROFILE } from "i18n/namespaces";
import { User } from "proto/api_pb";
import makeStyles from "utils/makeStyles";

import { useRegions } from "../hooks/useRegions";
import {
  LabelsAgeGenderLanguages,
  RemainingAboutLabels,
} from "./UserTextAndLabel";

interface AboutProps {
  user: User.AsObject;
}
const useStyles = makeStyles((theme) => ({
  root: {
    marginTop: theme.spacing(1),
  },
  marginTop3: {
    marginTop: theme.spacing(3),
  },
}));

export default function About({ user }: AboutProps) {
  const classes = useStyles();
  const { regions } = useRegions();
  const { t } = useTranslation([PROFILE, GLOBAL]);
  return (
    <div className={classes.root}>
      <Typography variant="h1">{t("global:overview")}</Typography>
      <LabelsAgeGenderLanguages user={user} />
      <RemainingAboutLabels user={user} />
      <Divider className={classes.marginTop3} />
      {user.aboutMe && (
        <>
          <Typography variant="h1">{t("global:who")}</Typography>
          <Markdown source={user.aboutMe} />
          <Divider className={classes.marginTop3} />
        </>
      )}
      {user.thingsILike && (
        <>
          <Typography variant="h1">{t("global:hobbies")}</Typography>
          <Markdown source={user.thingsILike} />
          <Divider className={classes.marginTop3} />
        </>
      )}
      {user.additionalInformation && (
        <>
          <Typography variant="h1">{t("global:additional")}</Typography>
          <Markdown source={user.additionalInformation} />
          <Divider className={classes.marginTop3} />
        </>
      )}
      <Typography variant="h1">{t("global:traveled_to")}</Typography>
      <Typography variant="body1">
        {regions && user.regionsVisitedList.length > 0
          ? user.regionsVisitedList
              .map((country) => regions[country])
              .join(`, `)
          : NONE}
      </Typography>
      <Divider className={classes.marginTop3} />
      <Typography variant="h1">{t("global:lived_in")}</Typography>
      <Typography variant="body1">
        {regions && user.regionsLivedList.length > 0
          ? user.regionsLivedList.map((country) => regions[country]).join(`, `)
          : NONE}
      </Typography>
    </div>
  );
}
